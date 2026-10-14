"""Interactive CLI prototype for Socratic DSA tutoring (Milestone 1.3).

Connects:
- Verified DSA Problem Catalog (backend/eval/dataset.py)
- Trusted Local C++ Test Runner & Deterministic Judge (backend/runner/cpp_runner.py)
- Qwen 3.5 4B Socratic Pedagogy Engine (backend/core/ollama_client.py)
"""

import asyncio
import os
import sys
import time
from typing import Optional, List

from backend.runner.cpp_runner import CppRunner
from backend.runner.schemas import TestVerdict, ExecutionReport
from backend.core.ollama_client import OllamaClient
from backend.core.tutor import Tutor
from backend.db.repository import create_practice_session, record_session_hint
from backend.core.schemas import HintLevel, ProgressiveHintResponse, MistakeDiagnosisResponse
from backend.eval.dataset import EVALUATION_DATASET, EvalProblem


class SocraticCliApp:
    """Terminal application facilitating Socratic DSA practice sessions."""

    def __init__(self, runner: Optional[CppRunner] = None, tutor: Optional[Tutor] = None, *, trusted_local_code: bool = False, connection=None):
        self.trusted_local_code = trusted_local_code
        self.connection = connection
        self.session_id = None
        self.runner = runner or CppRunner()
        self.tutor = tutor or OllamaClient()
        self.problems = EVALUATION_DATASET
        self.active_problem: Optional[EvalProblem] = None
        self.current_code: Optional[str] = None
        self.last_report: Optional[ExecutionReport] = None
        self.unlocked_hint_level: int = 0

    def list_problems(self) -> List[EvalProblem]:
        return self.problems

    def select_problem(self, index: int) -> EvalProblem:
        if 0 <= index < len(self.problems):
            self.active_problem = self.problems[index]
            self.session_id = create_practice_session(self.connection, self.active_problem.id) if self.connection is not None else None
            self.unlocked_hint_level = 0
            self.last_report = None
            self.current_code = None
            return self.active_problem
        raise IndexError(f"Problem index {index} out of range (0..{len(self.problems)-1})")

    def format_problem_display(self) -> str:
        p = self.active_problem
        if not p:
            return "No problem currently selected."

        examples_str = ""
        for i, tc in enumerate(p.test_cases[:2], 1):
            examples_str += f"\n  Example {i}:\n    Input: {tc.input_data.strip()}\n    Output: {tc.expected_output.strip()}\n"

        return f"""
================================================================================
PROBLEM: #{p.leetcode_id} — {p.title}
================================================================================
Target:     {p.target_complexity}

DESCRIPTION:
{p.description}

CONSTRAINTS:
{p.constraints}

EXAMPLES:
{examples_str}
EXPECTED FUNCTION SIGNATURE (C++):
{p.function_signature};
================================================================================
"""

    def submit_code(self, code_content: str) -> ExecutionReport:
        """Evaluates student C++ code using trusted local CppRunner."""
        if not self.active_problem:
            raise ValueError("No problem selected.")

        if not self.trusted_local_code:
            raise PermissionError("Trusted local code mode must be explicitly enabled; no sandbox is available")
        self.current_code = code_content
        full_source = self.active_problem.harness_template.replace(
            "// STUDENT_CODE_PLACEHOLDER",
            code_content
        )
        self.last_report = self.runner.run_test_suite(full_source, self.active_problem.test_cases, trusted=True)
        return self.last_report

    def format_verdict_display(self, report: ExecutionReport) -> str:
        """Renders formatted test verdict and timing statistics."""
        v = report.overall_verdict
        banner = ""
        if v == TestVerdict.AC:
            banner = f"[ACCEPTED - AC] Passed all {report.total_tests} tests in the available verified suite. This is not a proof for all inputs."
        elif v == TestVerdict.WA:
            banner = f"[WRONG ANSWER - WA] Passed {report.passed_tests}/{report.total_tests} test cases."
        elif v == TestVerdict.TLE:
            banner = f"[TIME LIMIT EXCEEDED - TLE] Execution timed out."
        elif v == TestVerdict.COMPILATION_ERROR:
            banner = f"[COMPILATION ERROR] g++ failed to compile code."
        elif v in (TestVerdict.OUTPUT_LIMIT, TestVerdict.MEMORY_LIMIT):
            banner = f"[RESOURCE LIMIT - {v.value}] Execution stopped."
        elif v == TestVerdict.RUNTIME_ERROR:
            banner = f"[RUNTIME ERROR] Process crashed or exited non-zero."

        timing = f"Compile Time: {report.compilation_time_ms:.1f}ms"
        if report.test_results:
            total_exec = sum(t.execution_time_ms for t in report.test_results)
            timing += f" | Test Execution Time: {total_exec:.1f}ms"

        details = ""
        if report.failing_evidence:
            details = f"\nEvidence of Failure:\n{report.failing_evidence.strip()}\n"

        return f"\n{'-'*60}\n{banner}\n{timing}\n{details}{'-'*60}\n"

    async def request_socratic_diagnosis(self) -> Optional[MistakeDiagnosisResponse]:
        """Queries Qwen 3.5 4B to diagnose the failure without revealing code."""
        if not self.active_problem or not self.last_report or not self.current_code:
            return None
        if self.last_report.overall_verdict == TestVerdict.AC:
            return None

        evidence = self.last_report.failing_evidence or "Code execution failed."
        try:
            diagnosis = await self.tutor.diagnose_mistake(
                problem_title=self.active_problem.title,
                problem_description=self.active_problem.description,
                target_complexity=self.active_problem.target_complexity,
                student_code=self.current_code,
                test_failure_evidence=evidence
            )
            return diagnosis
        except Exception as e:
            # Fallback gracefully
            return MistakeDiagnosisResponse(
                category="other", # type: ignore
                misconception_summary=f"Automated tutor feedback unavailable: {str(e)}",
                guiding_question="Review the failing test case input and trace your variable states step-by-step.",
                suggested_focus_area="Loop condition and variable state updates"
            )

    async def request_progressive_hint(self, level: int) -> ProgressiveHintResponse:
        """Requests progressive hint level (1..5)."""
        if not self.active_problem:
            raise ValueError("No problem selected.")

        target_level = HintLevel(level)
        if level > self.unlocked_hint_level + 1:
            raise ValueError('Unlock hint levels sequentially')
        try:
            hint = await self.tutor.get_progressive_hint(
                level=target_level, problem_title=self.active_problem.title,
                problem_description=self.active_problem.description,
                constraints=self.active_problem.constraints,
                primary_pattern=self.active_problem.primary_pattern,
                subpattern=self.active_problem.subpattern,
                function_signature=self.active_problem.function_signature)
            # Validate at the provider-neutral boundary as well as inside Ollama.
            hint = ProgressiveHintResponse.model_validate(hint.model_dump())
            if hint.level != target_level:
                raise ValueError('Tutor returned the wrong hint level')
        except Exception:
            if level == 1:
                # A fixed neutral nudge; no exception/model text can reveal a pattern.
                return ProgressiveHintResponse(level=target_level, title='Tutor unavailable',
                    guidance='Review the input constraints and compare them with the work your current approach performs. Retry this hint when the tutor is available.',
                    guiding_question='Which input property could help reduce repeated work?', contains_code=False)
            raise ValueError('Tutor unavailable or invalid response; this hint was not unlocked')
        if self.connection is not None:
            record_session_hint(self.connection, self.session_id, level)
        self.unlocked_hint_level = max(self.unlocked_hint_level, level)
        return hint


async def run_terminal_session(*, trusted_local_code=False):
    """Terminal loop for interactive student practice."""
    app = SocraticCliApp(trusted_local_code=trusted_local_code)

    print("\n" + "=" * 60)
    print("  AI CODING MENTOR — LOCAL Socratic DSA CLI (Milestone 1.3)")
    print("=" * 60)

    print("Execution is restricted to code you authored or reviewed and explicitly trust. Host resources are not isolated.")
    if not trusted_local_code:
        print("Submission disabled. Use --trusted-local only for explicitly trusted code.")

    # Check Ollama connection
    healthy = await app.tutor.check_health()
    if healthy:
        print("[✓] Ollama connected: configured model is available.")
    else:
        print("[!] Warning: Ollama is not reachable at http://localhost:11434. Running in offline fallback mode.")

    while True:
        print("\nAvailable Placement Problems:")
        for idx, p in enumerate(app.list_problems()):
            print(f"  [choice {idx + 1}] #{p.leetcode_id} — {p.title} ")
        print("  [0] Exit")

        choice = input("\nSelect a problem number: ").strip()
        if choice == "0":
            print("Exiting Socratic CLI. Happy coding!")
            break

        try:
            p_idx = int(choice) - 1
            app.select_problem(p_idx)
        except (ValueError, IndexError):
            print("Invalid selection. Please choose a valid problem number.")
            continue

        print(app.format_problem_display())

        # Sub-loop for problem solving and hints
        while True:
            print("\nOptions for current problem:")
            print("  [1] Submit C++ Code from a local file")
            print("  [2] Submit C++ Code directly (multiline paste)")
            print(f"  [3] Request Progressive Hint (Currently unlocked: Level {app.unlocked_hint_level}/5)")
            print("  [4] View Problem Statement Again")
            print("  [5] Choose Another Problem")

            sub_choice = input("\nEnter option (1-5): ").strip()

            if sub_choice == "5":
                break
            elif sub_choice == "4":
                print(app.format_problem_display())
            elif sub_choice in ("1", "2"):
                if not app.trusted_local_code:
                    print("Execution disabled: launch with --trusted-local for reviewed local code.")
                    continue
                code_text = ""
                if sub_choice == "1":
                    path = input("Enter path to C++ file: ").strip().strip('"').strip("'")
                    if not os.path.exists(path):
                        print(f"File not found: {path}")
                        continue
                    with open(path, "r", encoding="utf-8") as f:
                        code_text = f.read()
                else:
                    print("Paste your C++ function below (enter 'END' on a new line when finished):")
                    lines = []
                    while True:
                        try:
                            line = input()
                            if line.strip() == "END":
                                break
                            lines.append(line)
                        except EOFError:
                            break
                    code_text = "\n".join(lines)

                if not code_text.strip():
                    print("No code entered. Aborting submission.")
                    continue

                print("\nCompiling and running against verified test cases...")
                report = app.submit_code(code_text)
                print(app.format_verdict_display(report))

                # If failed, offer Socratic diagnosis
                if report.overall_verdict != TestVerdict.AC:
                    print("\n[AI Mentor] Analyzing failure evidence...")
                    start_t = time.perf_counter()
                    diag = await app.request_socratic_diagnosis()
                    latency_s = time.perf_counter() - start_t
                    if diag:
                        print(f"\n{'-'*60}")
                        print(f"SOCRATIC DIAGNOSIS ({diag.category.value}) - Generated in {latency_s:.1f}s:")
                        print(f"Misconception: {diag.misconception_summary}")
                        print(f"Guiding Question: {diag.guiding_question}")
                        print(f"Focus Area: {diag.suggested_focus_area}")
                        print(f"{'-'*60}\n")
                else:
                    print("\n🎉 Your solution passed the available verified suite.")

            elif sub_choice == "3":
                next_level = min(5, app.unlocked_hint_level + 1)
                lvl_names = {
                    1: "Level 1: Conceptual Nudge",
                    2: "Level 2: Pattern & Subpattern Clue",
                    3: "Level 3: Algorithmic Direction",
                    4: "Level 4: Structured Pseudocode",
                    5: "Level 5: Complete Reference Solution & Big-O"
                }
                confirm = input(f"Unlock {lvl_names[next_level]}? (y/n): ").strip().lower()
                if confirm == "y":
                    print(f"\nRequesting {lvl_names[next_level]} from Qwen 3.5 4B...")
                    start_t = time.perf_counter()
                    try:
                        hint = await app.request_progressive_hint(next_level)
                    except ValueError as exc:
                        print(str(exc))
                        continue
                    latency_s = time.perf_counter() - start_t
                    print(f"\n{'-'*60}")
                    print(f"[{hint.title}] ({latency_s:.1f}s)")
                    print(f"\n{hint.guidance}\n")
                    for field in ('pseudocode', 'code', 'explanation', 'time_complexity', 'space_complexity'):
                        value = getattr(hint, field)
                        if value:
                            print(value)
                    if hint.guiding_question:
                        print(f"Reflect on this: {hint.guiding_question}\n")
                    print(f"{'-'*60}")
            else:
                print("Invalid option.")


if __name__ == "__main__":
    asyncio.run(run_terminal_session())
