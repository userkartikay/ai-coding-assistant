"""Data access layer — thin repository over the SQLite schema.

All public methods accept an open sqlite3.Connection (injected by callers)
so that tests can use in-memory databases without file I/O.
"""

import json
import sqlite3
from functools import wraps
from typing import List, Optional

from backend.runner.schemas import ExecutionReport, TestVerdict



def atomic_write(fn):
    """Savepoint rollback also preserves an enclosing caller transaction."""
    @wraps(fn)
    def wrapped(conn, *args, **kwargs):
        conn.execute('SAVEPOINT repository_write')
        try:
            result = fn(conn, *args, **kwargs)
            conn.execute('RELEASE repository_write')
            return result
        except BaseException:
            if conn.in_transaction:
                conn.execute('ROLLBACK TO repository_write')
                conn.execute('RELEASE repository_write')
            raise
    return wrapped


def resolve_problem_id(conn, problem_id):
    row = conn.execute('SELECT problem_id FROM problem_aliases WHERE alias_id=?', (problem_id,)).fetchone()
    return row[0] if row else problem_id


# ---------------------------------------------------------------------------
# Problem repository
# ---------------------------------------------------------------------------

@atomic_write
def upsert_problem(conn: sqlite3.Connection, problem: dict) -> None:
    """Insert or update metadata without replacing the referenced row.

    problem dict keys mirror the `problems` table columns.
    """
    conn.execute(
        """
        INSERT INTO problems (
            id, leetcode_id, title, difficulty,
            primary_pattern, subpattern, secondary_patterns,
            prerequisites, time_complexity_target, space_complexity_target,
            educational_utility, official_link, provenance,
            verification_status, previously_solved
        ) VALUES (
            :id, :leetcode_id, :title, :difficulty,
            :primary_pattern, :subpattern, :secondary_patterns,
            :prerequisites, :time_complexity_target, :space_complexity_target,
            :educational_utility, :official_link, :provenance,
            :verification_status, :previously_solved
        ) ON CONFLICT(id) DO UPDATE SET
            leetcode_id=excluded.leetcode_id, title=excluded.title, difficulty=excluded.difficulty,
            primary_pattern=excluded.primary_pattern, subpattern=excluded.subpattern,
            secondary_patterns=excluded.secondary_patterns, prerequisites=excluded.prerequisites,
            time_complexity_target=excluded.time_complexity_target,
            space_complexity_target=excluded.space_complexity_target,
            educational_utility=excluded.educational_utility, official_link=excluded.official_link,
            provenance=excluded.provenance, verification_status=excluded.verification_status,
            previously_solved=MAX(problems.previously_solved,excluded.previously_solved)
        """,
        problem,
    )


def get_problem(conn: sqlite3.Connection, problem_id: str) -> Optional[sqlite3.Row]:
    """Fetch a problem row by its ID. Returns None if not found."""
    return conn.execute(
        "SELECT * FROM problems WHERE id = ?", (resolve_problem_id(conn, problem_id),)
    ).fetchone()


def list_problems(
    conn: sqlite3.Connection,
    pattern: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> List[sqlite3.Row]:
    """List problems with optional filtering by pattern or difficulty."""
    clauses, params = [], []
    if pattern:
        clauses.append("primary_pattern LIKE ?")
        params.append(f"%{pattern}%")
    if difficulty:
        clauses.append("difficulty = ?")
        params.append(difficulty)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return conn.execute(
        f"SELECT * FROM problems {where} ORDER BY primary_pattern, title",
        params,
    ).fetchall()


# ---------------------------------------------------------------------------
# Attempt repository
# ---------------------------------------------------------------------------

@atomic_write
def save_attempt(
    conn: sqlite3.Connection,
    problem_id: str,
    submitted_code: str,
    report: ExecutionReport,
    session_id: Optional[int] = None,
) -> int:
    """Persist an attempt and its per-test results. Returns the new attempt ID."""
    problem_id = resolve_problem_id(conn, problem_id)
    if session_id is not None:
        session = conn.execute('SELECT problem_id FROM practice_sessions WHERE id=?', (session_id,)).fetchone()
        if session is None or session[0] != problem_id:
            raise ValueError('Session must belong to the submitted problem')
    cur = conn.execute(
        """
        INSERT INTO attempts (
            problem_id, session_id, submitted_code, overall_verdict,
            passed_tests, total_tests, compile_ms, run_ms, compiler_stderr
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            problem_id,
            session_id,
            submitted_code,
            report.overall_verdict.value,
            report.passed_tests,
            report.total_tests,
            report.compilation_time_ms,
            sum(tr.execution_time_ms for tr in report.test_results),
            report.compilation_output,  # contains compiler stderr when compilation fails
        ),
    )
    attempt_id = cur.lastrowid

    for idx, tr in enumerate(report.test_results):
        conn.execute(
            """
            INSERT INTO test_results (attempt_id, test_index, verdict, input_data, expected, actual, stderr)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                idx,
                tr.verdict.value,
                tr.input_data,
                tr.expected_output,
                tr.actual_output,
                tr.error_message,
            ),
        )

    return attempt_id


def get_attempts_for_problem(
    conn: sqlite3.Connection, problem_id: str, limit: int = 50
) -> List[sqlite3.Row]:
    """Return recent attempts for a problem, newest first."""
    return conn.execute(
        """
        SELECT * FROM attempts
        WHERE problem_id = ?
        ORDER BY submitted_at DESC, id DESC
        LIMIT ?
        """,
        (resolve_problem_id(conn, problem_id), limit),
    ).fetchall()


def get_attempt(conn: sqlite3.Connection, attempt_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM attempts WHERE id = ?", (attempt_id,)
    ).fetchone()


# ---------------------------------------------------------------------------
# Hint tracking
# ---------------------------------------------------------------------------

@atomic_write
def record_hint_access(
    conn: sqlite3.Connection, attempt_id: int, hint_level: int
) -> None:
    """Log that a student unlocked a particular hint level during an attempt."""
    conn.execute(
        "INSERT INTO hints_accessed (attempt_id, hint_level) VALUES (?, ?)",
        (attempt_id, hint_level),
    )


def get_hints_accessed(
    conn: sqlite3.Connection, attempt_id: int
) -> List[int]:
    """Return list of hint levels accessed for an attempt, in order."""
    rows = conn.execute(
        "SELECT hint_level FROM hints_accessed WHERE attempt_id = ? ORDER BY accessed_at, id",
        (attempt_id,),
    ).fetchall()
    return [r["hint_level"] for r in rows]


# ---------------------------------------------------------------------------
# Diagnosis tracking
# ---------------------------------------------------------------------------

@atomic_write
def save_diagnosis(
    conn: sqlite3.Connection,
    attempt_id: int,
    mistake_category: str,
    tutor_question: str,
    raw_response: Optional[str] = None,
    latency_ms: Optional[float] = None,
) -> int:
    """Persist a tutor diagnosis for an attempt."""
    cur = conn.execute(
        """
        INSERT INTO diagnoses (attempt_id, mistake_category, tutor_question, raw_response, latency_ms)
        VALUES (?, ?, ?, ?, ?)
        """,
        (attempt_id, mistake_category, tutor_question, raw_response, latency_ms),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Summary queries
# ---------------------------------------------------------------------------

def get_problem_summary(conn: sqlite3.Connection, problem_id: str) -> dict:
    """Return attempt statistics for a problem."""
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_attempts,
            SUM(CASE WHEN overall_verdict = 'AC' THEN 1 ELSE 0 END) AS ac_count,
            MAX(passed_tests * 1.0 / NULLIF(total_tests, 0)) AS best_pass_rate
        FROM attempts WHERE problem_id = ?
        """,
        (resolve_problem_id(conn, problem_id),),
    ).fetchone()
    return dict(row) if row else {}


def get_weakest_patterns(conn: sqlite3.Connection, top_n: int = 5) -> List[dict]:
    """Return patterns with the highest WA/TLE/RTE rate, ordered by failure rate."""
    rows = conn.execute(
        """
        SELECT
            p.primary_pattern,
            COUNT(a.id) AS total,
            SUM(CASE WHEN a.overall_verdict != 'AC' THEN 1 ELSE 0 END) AS failures,
            ROUND(SUM(CASE WHEN a.overall_verdict != 'AC' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 1) AS failure_pct
        FROM attempts a
        JOIN problems p ON p.id = a.problem_id
        GROUP BY p.primary_pattern
        HAVING total >= 2
        ORDER BY failure_pct DESC
        LIMIT ?
        """,
        (top_n,),
    ).fetchall()
    return [dict(r) for r in rows]


@atomic_write
def create_practice_session(conn: sqlite3.Connection, problem_id: str) -> int:
    return conn.execute('INSERT INTO practice_sessions(problem_id) VALUES (?)',
                        (resolve_problem_id(conn, problem_id),)).lastrowid


@atomic_write
def record_session_hint(conn: sqlite3.Connection, session_id: int, hint_level: int) -> None:
    conn.execute('INSERT INTO session_hints(session_id,hint_level) VALUES (?,?)',
                 (session_id, hint_level))


def get_session_hints(conn: sqlite3.Connection, session_id: int) -> List[int]:
    return [r[0] for r in conn.execute(
        'SELECT hint_level FROM session_hints WHERE session_id=? ORDER BY accessed_at,id',
        (session_id,))]
