"""Test suite verifying integrity of the DSA evaluation dataset against CppRunner."""

import pytest
from backend.runner.cpp_runner import CppRunner
from backend.runner.schemas import TestVerdict
from backend.eval.dataset import EVALUATION_DATASET


@pytest.fixture
def runner():
    return CppRunner(compile_timeout=5.0, test_timeout=2.0)


def test_dataset_contains_at_least_five_examples():
    """Verify evaluation dataset has at least 5 carefully verified examples."""
    assert len(EVALUATION_DATASET) >= 5


@pytest.mark.parametrize("problem", EVALUATION_DATASET, ids=lambda p: p.id)
def test_canonical_solutions_pass(runner, problem):
    """Verify that every canonical reference solution compiles and passes all test cases."""
    source = problem.harness_template.replace("// STUDENT_CODE_PLACEHOLDER", problem.canonical_solution)
    report = runner.run_test_suite(source, problem.test_cases, trusted=True)
    assert report.compilation_success is True, f"Compilation failed for {problem.id}: {report.compilation_output}"
    assert report.overall_verdict == TestVerdict.AC, f"Expected AC for {problem.id}, got {report.overall_verdict}"
    assert report.passed_tests == len(problem.test_cases)


@pytest.mark.parametrize("problem", EVALUATION_DATASET, ids=lambda p: p.id)
def test_buggy_solutions_fail(runner, problem):
    """Verify that every buggy submission fails deterministically and produces failing evidence."""
    source = problem.harness_template.replace("// STUDENT_CODE_PLACEHOLDER", problem.buggy_submission)
    report = runner.run_test_suite(source, problem.test_cases, trusted=True)
    assert report.overall_verdict != TestVerdict.AC, f"Buggy code unexpectedly passed for {problem.id}"
    assert report.failing_evidence is not None, f"Expected failing evidence for {problem.id}"
