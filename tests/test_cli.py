"""Automated integration tests for Socratic CLI prototype (Milestone 1.3)."""

import pytest
from backend.cli.interactive_cli import SocraticCliApp
from backend.runner.schemas import TestVerdict
from backend.core.schemas import HintLevel


def test_cli_problem_selection():
    app = SocraticCliApp(trusted_local_code=True)
    problems = app.list_problems()
    assert len(problems) >= 5

    p0 = app.select_problem(0)
    assert p0.id == "lc_167"
    assert app.active_problem == p0

    display_text = app.format_problem_display()
    assert "Two Sum II" in display_text
    assert "Pattern:" not in display_text
    assert "vector<int> twoSum" in display_text


def test_cli_submit_ac():
    app = SocraticCliApp(trusted_local_code=True)
    p = app.select_problem(0)
    report = app.submit_code(p.canonical_solution)
    assert report.overall_verdict == TestVerdict.AC
    assert report.passed_tests == len(p.test_cases)

    verdict_text = app.format_verdict_display(report)
    assert "[ACCEPTED - AC]" in verdict_text
    assert "Compile Time:" in verdict_text


def test_cli_submit_wa_and_evidence():
    app = SocraticCliApp(trusted_local_code=True)
    p = app.select_problem(0)
    report = app.submit_code(p.buggy_submission)
    assert report.overall_verdict == TestVerdict.WA
    assert report.failing_evidence is not None

    verdict_text = app.format_verdict_display(report)
    assert "[WRONG ANSWER - WA]" in verdict_text
    assert "Evidence of Failure:" in verdict_text


@pytest.mark.asyncio
async def test_cli_socratic_diagnosis_flow():
    app = SocraticCliApp(trusted_local_code=True)
    healthy = await app.tutor.check_health()
    if not healthy:
        pytest.skip("Ollama offline.")

    p = app.select_problem(0)
    # Submit buggy code
    app.submit_code(p.buggy_submission)
    diag = await app.request_socratic_diagnosis()
    assert diag is not None
    assert len(diag.misconception_summary) > 5
    assert len(diag.guiding_question) > 5


@pytest.mark.asyncio
async def test_cli_progressive_hint_flow():
    app = SocraticCliApp(trusted_local_code=True)
    healthy = await app.tutor.check_health()
    if not healthy:
        pytest.skip("Ollama offline.")

    app.select_problem(0)
    h1 = await app.request_progressive_hint(1)
    assert h1.level == HintLevel.LEVEL_1_NUDGE
    assert app.unlocked_hint_level == 1
    assert h1.contains_code is False

    h2 = await app.request_progressive_hint(2)
    assert h2.level == HintLevel.LEVEL_2_PATTERN
    assert app.unlocked_hint_level == 2


def test_cli_revise_and_resubmit_workflow():
    """Verify that a student can submit buggy code, get failure verdict, revise, and achieve AC."""
    app = SocraticCliApp(trusted_local_code=True)
    p = app.select_problem(0)

    # 1. First submission (buggy)
    rep1 = app.submit_code(p.buggy_submission)
    assert rep1.overall_verdict == TestVerdict.WA

    # 2. Student revises and submits canonical solution
    rep2 = app.submit_code(p.canonical_solution)
    assert rep2.overall_verdict == TestVerdict.AC
    assert rep2.passed_tests == len(p.test_cases)
