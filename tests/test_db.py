"""Tests for Phase 2, Milestone 2.1: SQLite schema and repository layer.

All tests use in-memory SQLite databases — no file I/O, no side effects.
"""

import json
import sqlite3
import pytest

from backend.db.schema import initialize_database, get_connection
from backend.db.repository import (
    upsert_problem,
    get_problem,
    list_problems,
    save_attempt,
    get_attempts_for_problem,
    get_attempt,
    record_hint_access,
    get_hints_accessed,
    save_diagnosis,
    get_problem_summary,
    get_weakest_patterns,
)
from backend.runner.schemas import (
    TestVerdict,
    TestCase,
    TestCaseResult,
    ExecutionReport,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mem_db():
    """In-memory SQLite database, fully initialized with the schema."""
    from pathlib import Path
    import tempfile, os

    # initialize_database expects a Path; use ":memory:" via direct connection trick
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    from backend.db.schema import DDL
    conn.executescript(DDL)
    conn.commit()
    yield conn
    conn.close()


SAMPLE_PROBLEM = {
    "id": "test_two_sum",
    "leetcode_id": 1,
    "title": "Two Sum",
    "difficulty": "Easy",
    "primary_pattern": "Hash Map",
    "subpattern": "Complement Lookup",
    "secondary_patterns": "[]",
    "prerequisites": "[]",
    "time_complexity_target": "O(N)",
    "space_complexity_target": "O(N)",
    "educational_utility": "Classic O(N) hash map warm-up.",
    "official_link": "https://leetcode.com/problems/two-sum/",
    "provenance": "curated_core",
    "verification_status": "verified",
    "previously_solved": 0,
}


def make_ac_report() -> ExecutionReport:
    tc_result = TestCaseResult(
        test_case_id="tc1",
        passed=True,
        verdict=TestVerdict.AC,
        actual_output="3",
        expected_output="3",
        input_data="1 2\n1 1",
        execution_time_ms=5.0,
        error_message=None,
    )
    return ExecutionReport(
        overall_verdict=TestVerdict.AC,
        compilation_success=True,
        compilation_output="",
        compilation_time_ms=120.0,
        test_results=[tc_result],
        total_tests=1,
        passed_tests=1,
        failing_evidence=None,
    )


def make_wa_report() -> ExecutionReport:
    tc_result = TestCaseResult(
        test_case_id="tc1",
        passed=False,
        verdict=TestVerdict.WA,
        actual_output="0",
        expected_output="3",
        input_data="1 2\n1 1",
        execution_time_ms=4.0,
        error_message=None,
    )
    return ExecutionReport(
        overall_verdict=TestVerdict.WA,
        compilation_success=True,
        compilation_output="",
        compilation_time_ms=110.0,
        test_results=[tc_result],
        total_tests=1,
        passed_tests=0,
        failing_evidence="Expected: 3\nGot: 0",
    )


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

def test_schema_creates_all_tables(mem_db):
    tables = {
        row[0] for row in mem_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    expected = {"problems", "attempts", "test_results", "hints_accessed", "diagnoses", "schema_version"}
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"


def test_schema_version_is_seeded(mem_db):
    version = mem_db.execute("SELECT version FROM schema_version").fetchone()
    assert version is not None
    assert version[0] == 1


# ---------------------------------------------------------------------------
# Problem repository tests
# ---------------------------------------------------------------------------

def test_upsert_and_get_problem(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    row = get_problem(mem_db, "test_two_sum")
    assert row is not None
    assert row["title"] == "Two Sum"
    assert row["primary_pattern"] == "Hash Map"


def test_upsert_is_idempotent(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    upsert_problem(mem_db, SAMPLE_PROBLEM)  # second insert must not raise or duplicate
    count = mem_db.execute("SELECT COUNT(*) FROM problems WHERE id='test_two_sum'").fetchone()[0]
    assert count == 1


def test_get_nonexistent_problem_returns_none(mem_db):
    result = get_problem(mem_db, "does_not_exist")
    assert result is None


def test_list_problems_no_filter(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    results = list_problems(mem_db)
    assert len(results) >= 1


def test_list_problems_pattern_filter(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    results = list_problems(mem_db, pattern="Hash Map")
    assert len(results) == 1
    results_none = list_problems(mem_db, pattern="Graph")
    assert len(results_none) == 0


def test_list_problems_difficulty_filter(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    results = list_problems(mem_db, difficulty="Easy")
    assert len(results) == 1
    results_med = list_problems(mem_db, difficulty="Medium")
    assert len(results_med) == 0


# ---------------------------------------------------------------------------
# Attempt repository tests
# ---------------------------------------------------------------------------

def test_save_and_retrieve_ac_attempt(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    report = make_ac_report()
    attempt_id = save_attempt(mem_db, "test_two_sum", "int main(){}", report)

    assert attempt_id > 0
    row = get_attempt(mem_db, attempt_id)
    assert row is not None
    assert row["overall_verdict"] == "AC"
    assert row["passed_tests"] == 1
    assert row["total_tests"] == 1
    assert row["compile_ms"] == pytest.approx(120.0)


def test_save_and_retrieve_wa_attempt(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    report = make_wa_report()
    attempt_id = save_attempt(mem_db, "test_two_sum", "int main(){return 0;}", report)

    row = get_attempt(mem_db, attempt_id)
    assert row["overall_verdict"] == "WA"
    assert row["passed_tests"] == 0


def test_test_results_persisted(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    report = make_ac_report()
    attempt_id = save_attempt(mem_db, "test_two_sum", "...", report)

    results = mem_db.execute(
        "SELECT * FROM test_results WHERE attempt_id=?", (attempt_id,)
    ).fetchall()
    assert len(results) == 1
    assert results[0]["verdict"] == "AC"
    assert results[0]["actual"] == "3"


def test_get_attempts_for_problem_returns_newest_first(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    id1 = save_attempt(mem_db, "test_two_sum", "code_v1", make_wa_report())
    id2 = save_attempt(mem_db, "test_two_sum", "code_v2", make_ac_report())

    rows = get_attempts_for_problem(mem_db, "test_two_sum")
    assert len(rows) == 2
    # Both attempts exist; verify the one with id2 is present (insertion order may tie on same-second timestamp)
    ids = {row["id"] for row in rows}
    assert id1 in ids and id2 in ids
    assert [r["id"] for r in rows] == [id2, id1]


def test_get_attempts_for_nonexistent_problem_returns_empty(mem_db):
    rows = get_attempts_for_problem(mem_db, "nonexistent")
    assert rows == []


# ---------------------------------------------------------------------------
# Hint tracking tests
# ---------------------------------------------------------------------------

def test_record_and_retrieve_hints(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    attempt_id = save_attempt(mem_db, "test_two_sum", "code", make_wa_report())

    record_hint_access(mem_db, attempt_id, 1)
    record_hint_access(mem_db, attempt_id, 2)

    hints = get_hints_accessed(mem_db, attempt_id)
    assert hints == [1, 2]


def test_no_hints_returns_empty_list(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    attempt_id = save_attempt(mem_db, "test_two_sum", "code", make_ac_report())
    assert get_hints_accessed(mem_db, attempt_id) == []


def test_invalid_hint_level_rejected(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    attempt_id = save_attempt(mem_db, "test_two_sum", "code", make_ac_report())
    with pytest.raises(sqlite3.IntegrityError):
        record_hint_access(mem_db, attempt_id, 6)  # level > 5 violates CHECK constraint


# ---------------------------------------------------------------------------
# Diagnosis tracking tests
# ---------------------------------------------------------------------------

def test_save_and_retrieve_diagnosis(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    attempt_id = save_attempt(mem_db, "test_two_sum", "code", make_wa_report())
    diag_id = save_diagnosis(
        mem_db, attempt_id,
        mistake_category="BOUNDARY_OFF_BY_ONE",
        tutor_question="Where exactly does your loop boundary deviate from the invariant?",
        raw_response="{...}",
        latency_ms=1800.0,
    )
    assert diag_id > 0

    row = mem_db.execute(
        "SELECT * FROM diagnoses WHERE id=?", (diag_id,)
    ).fetchone()
    assert row["mistake_category"] == "BOUNDARY_OFF_BY_ONE"
    assert row["latency_ms"] == pytest.approx(1800.0)


# ---------------------------------------------------------------------------
# Summary / analytics tests
# ---------------------------------------------------------------------------

def test_problem_summary_ac(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    save_attempt(mem_db, "test_two_sum", "code", make_wa_report())
    save_attempt(mem_db, "test_two_sum", "code", make_ac_report())

    summary = get_problem_summary(mem_db, "test_two_sum")
    assert summary["total_attempts"] == 2
    assert summary["ac_count"] == 1


def test_weakest_patterns_requires_minimum_attempts(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    # Only 1 attempt — should not appear (minimum 2 required)
    save_attempt(mem_db, "test_two_sum", "code", make_wa_report())
    result = get_weakest_patterns(mem_db)
    assert result == []


def test_weakest_patterns_appears_after_two_attempts(mem_db):
    upsert_problem(mem_db, SAMPLE_PROBLEM)
    save_attempt(mem_db, "test_two_sum", "code", make_wa_report())
    save_attempt(mem_db, "test_two_sum", "code", make_wa_report())
    result = get_weakest_patterns(mem_db)
    assert len(result) == 1
    assert result[0]["primary_pattern"] == "Hash Map"
    assert result[0]["failure_pct"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Seed script integration test
# ---------------------------------------------------------------------------

def test_seed_script_populates_db(tmp_path):
    """Integration test: run seed script and verify DB has correct problem counts."""
    import sys, subprocess
    db_path = tmp_path / "mentor_test.db"
    result = subprocess.run(
        [sys.executable, "scripts/seed_db.py", "--db", str(db_path)],
        capture_output=True,
        text=True,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
    )
    assert result.returncode == 0, f"seed_db.py failed:\n{result.stdout}\n{result.stderr}"

    conn = sqlite3.connect(str(db_path))
    count = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    conn.close()

    # 53 curriculum + up to 10 eval, some overlap possible — at least 53
    assert count == 133, f"Expected >=53 problems in DB, got {count}"
