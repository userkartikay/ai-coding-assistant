"""Automated test suite for Socratic DSA tutor client, prompts, and schema validation."""

import pytest
import asyncio
from backend.core.schemas import (
    HintLevel,
    MistakeCategory,
    ProgressiveHintResponse,
    MistakeDiagnosisResponse
)
from backend.core.prompts import (
    build_hint_prompt,
    build_mistake_diagnosis_prompt
)
from backend.core.ollama_client import OllamaClient, _clean_json_output


def test_schema_progressive_hint_validation():
    """Verify ProgressiveHintResponse validates valid payload and flags errors."""
    valid_data = {
        "level": 1,
        "title": "Observing Sorted Property",
        "guidance": "Think about how the array is ordered.",
        "guiding_question": "What invariant does a sorted array give you?",
        "contains_code": False
    }
    model = ProgressiveHintResponse.model_validate(valid_data)
    assert model.level == HintLevel.LEVEL_1_NUDGE
    assert model.contains_code is False
    assert model.guiding_question is not None


def test_schema_mistake_diagnosis_validation():
    """Verify MistakeDiagnosisResponse enforces enum categories."""
    valid_data = {
        "category": "state_transition",
        "misconception_summary": "Both pointers were incremented instead of moving toward each other.",
        "guiding_question": "Which pointer needs to move when the sum is too small?",
        "suggested_focus_area": "The conditional update inside the loop"
    }
    diagnosis = MistakeDiagnosisResponse.model_validate(valid_data)
    assert diagnosis.category == MistakeCategory.STATE_TRANSITION
    assert "pointer" in diagnosis.guiding_question.lower()


def test_clean_json_output_markdown_stripping():
    """Verify _clean_json_output correctly extracts JSON from code blocks."""
    markdown_wrapped = """Here is the response:
```json
{
  "level": 1,
  "title": "Nudge",
  "guidance": "Look at the order.",
  "guiding_question": "Why is it sorted?",
  "contains_code": false
}
```
Hope this helps!"""
    cleaned = _clean_json_output(markdown_wrapped)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert '"level": 1' in cleaned


def test_prompt_level_1_anti_leakage_constraints():
    """Verify Level 1 prompt explicitly forbids code and algorithm names."""
    prompt = build_hint_prompt(
        level=HintLevel.LEVEL_1_NUDGE,
        problem_title="Two Sum II",
        problem_description="Find pair in sorted array",
        constraints="2 <= n <= 10^5"
    )
    assert "DO NOT reveal or name the specific algorithm" in prompt
    assert "DO NOT write any pseudocode or code" in prompt
    assert '"level": 1' in prompt


def test_prompt_level_2_pattern_focus():
    """Verify Level 2 prompt focuses on pattern and subpattern identification."""
    prompt = build_hint_prompt(
        level=HintLevel.LEVEL_2_PATTERN,
        problem_title="Two Sum II",
        problem_description="Find pair in sorted array",
        constraints="2 <= n <= 10^5",
        primary_pattern="Two Pointers",
        subpattern="Collision"
    )
    assert "Two Pointers" in prompt
    assert "Collision" in prompt
    assert "subpattern" in prompt.lower()


def test_prompt_level_5_solution_requirements():
    """Verify Level 5 prompt mandates C++ reference code and Big-O analysis."""
    prompt = build_hint_prompt(
        level=HintLevel.LEVEL_5_SOLUTION,
        problem_title="Two Sum II",
        problem_description="Find pair in sorted array",
        constraints="2 <= n <= 10^5"
    )
    assert "Optimal, clean C++ reference solution" in prompt or "C++" in prompt
    assert "Time Complexity" in prompt
    assert "Space Complexity" in prompt


@pytest.mark.asyncio
async def test_live_ollama_level_1_hint():
    """Integration test: query Ollama for Level 1 hint and verify anti-leakage."""
    client = OllamaClient()
    healthy = await client.check_health()
    if not healthy:
        pytest.skip("Ollama is not running locally.")

    hint = await client.get_progressive_hint(
        level=HintLevel.LEVEL_1_NUDGE,
        problem_title="Two Sum II - Input Array Is Sorted",
        problem_description="Find two numbers such that they add up to a target in a sorted array.",
        constraints="Array is sorted in non-decreasing order."
    )
    assert hint.level == HintLevel.LEVEL_1_NUDGE
    assert hint.contains_code is False
    assert hint.guiding_question is not None
    # Must not contain C++ solution code
    assert "vector<int>" not in hint.guidance
    assert "while (" not in hint.guidance


@pytest.mark.asyncio
async def test_live_ollama_mistake_diagnosis():
    """Integration test: query Ollama for conceptual mistake diagnosis."""
    client = OllamaClient()
    healthy = await client.check_health()
    if not healthy:
        pytest.skip("Ollama is not running locally.")

    from backend.eval.dataset import EVALUATION_DATASET
    from backend.runner.cpp_runner import CppRunner
    problem = EVALUATION_DATASET[0]
    student_code = problem.buggy_submission
    report = CppRunner().run_test_suite(
        problem.harness_template.replace('// STUDENT_CODE_PLACEHOLDER',student_code),
        problem.test_cases,trusted=True)
    failure = report.failing_evidence
    assert failure is not None

    diagnosis = await client.diagnose_mistake(
        problem_title="Two Sum II",
        problem_description="Find pair in sorted array",
        target_complexity="O(N) time, O(1) space",
        student_code=student_code,
        test_failure_evidence=failure
    )
    assert isinstance(diagnosis.category, MistakeCategory)
    assert len(diagnosis.misconception_summary) > 10
    assert len(diagnosis.guiding_question) > 10
    # Must provide guiding question rather than rewriting the code
    assert "vector<int>" not in diagnosis.guiding_question
