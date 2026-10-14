"""Trusted local C++ execution runner and deterministic judge.

NOTE ON SAFETY & SECURITY:
This runner enforces runtime process safeguards (strict compilation/execution timeouts,
bounded output buffers, sampled RSS limits, and best-effort tempdir cleanup) for running TRUSTED local
test code. These safeguards limit observed runaway processes and retained output during local
development; sampled RSS limits do not guarantee allocation containment. They do NOT constitute a secure isolation sandbox for untrusted code.
Untrusted code execution is deferred until an isolated environment is implemented.
"""

import os
import subprocess
import tempfile
import time
from typing import List, Optional, Tuple
import psutil

from backend.runner.schemas import (
    TestVerdict,
    TestCase,
    TestCaseResult,
    ExecutionReport
)

MAX_OUTPUT_BYTES = 10 * 1024  # 10 KB output buffer bound
DEFAULT_COMPILE_TIMEOUT_SEC = 5.0
DEFAULT_TEST_TIMEOUT_SEC = 2.0


from backend.runner.process import run_bounded, kill_process_tree as _kill_process_tree


def _normalize_output(text: str) -> str:
    """Normalizes output by trimming whitespace and normalizing line breaks."""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines)


class CppRunner:
    """Executes trusted C++ source code against deterministic test cases."""

    def __init__(
        self,
        compiler_path: str = "g++",
        compile_timeout: float = DEFAULT_COMPILE_TIMEOUT_SEC,
        test_timeout: float = DEFAULT_TEST_TIMEOUT_SEC,
        max_output_bytes: int = MAX_OUTPUT_BYTES,
        memory_limit_mb: int = 256,
        compile_memory_limit_mb: int = 512,
    ):
        self.compiler_path = compiler_path
        self.compile_timeout = compile_timeout
        self.test_timeout = test_timeout
        if min(compile_timeout, test_timeout, max_output_bytes, memory_limit_mb, compile_memory_limit_mb) <= 0:
            raise ValueError("Resource limits must be positive")
        self.max_output_bytes = max_output_bytes
        self.memory_limit_mb = memory_limit_mb
        self.compile_memory_limit_mb = compile_memory_limit_mb

    def compile(self, source_code: str, work_dir: str, *, trusted: bool = False) -> Tuple[bool, str, Optional[str], float]:
        if not trusted:
            raise PermissionError('Only explicitly trusted local source may be compiled')
        source_file = os.path.join(work_dir, 'solution.cpp')
        exe_file = os.path.join(work_dir, 'solution.exe')
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(source_code)
        start = time.perf_counter()
        try:
            result = run_bounded([self.compiler_path, '-std=c++14', '-O2', source_file, '-o', exe_file],
                                 cwd=work_dir, timeout=self.compile_timeout,
                                 output_limit=self.max_output_bytes,
                                 memory_limit_mb=self.compile_memory_limit_mb)
            output = (result.stdout + '\n' + result.stderr).strip()
            if result.reason:
                output += f'\nCompilation stopped: {result.reason} limit or pipe error.'
            ok = result.returncode == 0 and result.reason is None and os.path.exists(exe_file)
            return ok, output, exe_file if ok else None, result.elapsed_ms
        except (OSError, RuntimeError) as exc:
            return False, f'Compiler unavailable or process error: {exc}', None, (time.perf_counter()-start)*1000

    def execute_test(self, exe_path: str, test_case: TestCase, *, trusted: bool = False) -> TestCaseResult:
        if not trusted:
            raise PermissionError('Only explicitly trusted local executables may run')
        start = time.perf_counter()
        try:
            result = run_bounded([exe_path], cwd=os.path.dirname(exe_path), input_data=test_case.input_data,
                                 timeout=self.test_timeout, output_limit=self.max_output_bytes,
                                 memory_limit_mb=self.memory_limit_mb)
            verdict = {'timeout': TestVerdict.TLE, 'output': TestVerdict.OUTPUT_LIMIT,
                       'memory': TestVerdict.MEMORY_LIMIT, 'io': TestVerdict.RUNTIME_ERROR}.get(result.reason)
            error = None
            if verdict:
                error = f'Execution stopped: {result.reason} limit or pipe error. Stderr: {result.stderr}'
            elif result.returncode != 0:
                verdict = TestVerdict.RUNTIME_ERROR
                error = f'Process exited with code {result.returncode}. Stderr: {result.stderr}'
            else:
                verdict = TestVerdict.AC if _normalize_output(result.stdout) == _normalize_output(test_case.expected_output) else TestVerdict.WA
            return TestCaseResult(test_case_id=test_case.id, passed=verdict == TestVerdict.AC,
                                  verdict=verdict, actual_output=result.stdout.strip(),
                                  input_data=test_case.input_data, expected_output=test_case.expected_output.strip(),
                                  execution_time_ms=result.elapsed_ms, error_message=error)
        except (OSError, RuntimeError) as exc:
            return TestCaseResult(test_case_id=test_case.id, passed=False, verdict=TestVerdict.RUNTIME_ERROR,
                                  input_data=test_case.input_data, expected_output=test_case.expected_output,
                                  execution_time_ms=(time.perf_counter()-start)*1000, error_message=str(exc))

    def run_test_suite(
        self,
        source_code: str,
        test_cases: List[TestCase],
        *, trusted: bool = False,
    ) -> ExecutionReport:
        """AC means all available verified tests passed; this is not a security sandbox."""
        if not test_cases:
            raise ValueError('A non-empty verified test suite is required')
        if not trusted:
            raise PermissionError('Explicit trusted=True is required; no untrusted execution supported')
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as work_dir:
            success, comp_out, exe_path, comp_time = self.compile(source_code, work_dir, trusted=True)

            if not success:
                failing_evidence = (
                    f"COMPILATION ERROR:\n"
                    f"Diagnostics:\n{comp_out}\n"
                )
                return ExecutionReport(
                    overall_verdict=TestVerdict.COMPILATION_ERROR,
                    compilation_success=False,
                    compilation_output=comp_out,
                    compilation_time_ms=comp_time,
                    test_results=[],
                    total_tests=len(test_cases),
                    passed_tests=0,
                    failing_evidence=failing_evidence
                )

            results: List[TestCaseResult] = []
            overall_verdict = TestVerdict.AC
            failing_evidence = None

            for tc in test_cases:
                tc_res = self.execute_test(exe_path, tc, trusted=True)
                results.append(tc_res)

                if not tc_res.passed and overall_verdict == TestVerdict.AC:
                    overall_verdict = tc_res.verdict
                    # Format evidence for tutor
                    if tc_res.verdict == TestVerdict.WA:
                        failing_evidence = (
                            f"FAILED TEST CASE: {tc_res.test_case_id}\n"
                            f"Input: {tc_res.input_data.strip()}\n"
                            f"Expected Output: {tc_res.expected_output}\n"
                            f"Actual Output: {tc_res.actual_output}\n"
                            f"Verdict: Wrong Answer (WA)\n"
                        )
                    elif tc_res.verdict == TestVerdict.TLE:
                        failing_evidence = (
                            f"FAILED TEST CASE: {tc_res.test_case_id}\n"
                            f"Input: {tc_res.input_data.strip()}\n"
                            f"Verdict: Time Limit Exceeded (TLE) - Possible infinite loop or suboptimal complexity.\n"
                        )
                    elif tc_res.verdict == TestVerdict.RUNTIME_ERROR:
                        failing_evidence = (
                            f"FAILED TEST CASE: {tc_res.test_case_id}\n"
                            f"Input: {tc_res.input_data.strip()}\n"
                            f"Verdict: Runtime Error (RTE)\n"
                            f"Diagnostics: {tc_res.error_message}\n"
                        )

                    else:
                        failing_evidence = f"FAILED TEST CASE: {tc_res.test_case_id}\nVerdict: {tc_res.verdict.value}\nDiagnostics: {tc_res.error_message}"

            passed_count = sum(1 for r in results if r.passed)
            return ExecutionReport(
                overall_verdict=overall_verdict,
                compilation_success=True,
                compilation_output=comp_out,
                compilation_time_ms=comp_time,
                test_results=results,
                total_tests=len(test_cases),
                passed_tests=passed_count,
                failing_evidence=failing_evidence
            )
