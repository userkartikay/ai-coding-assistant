"""SQLite schema and DDL for attempt persistence (Phase 2, Milestone 2.2 groundwork).

Tables:
  problems       — curriculum catalogue (seeded from CURATED_CATALOGUE)
  attempts       — each code submission event
  test_results   — per-test-case verdicts within an attempt
  hints_accessed — which hint levels were unlocked in an attempt

Design decisions:
  - Plain sqlite3 only (no ORM dependency). Keeps the stack simple and portable.
  - All timestamps stored as ISO-8601 text (UTC) for readability.
  - Foreign keys enabled per connection via PRAGMA.
  - Schema versioning via a 'schema_version' table for future migrations.
"""

import sqlite3
from pathlib import Path

# DDL -----------------------------------------------------------------------

DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Curriculum catalogue: one row per problem ----------------------------------
CREATE TABLE IF NOT EXISTS problems (
    id                      TEXT PRIMARY KEY,   -- e.g. "two_sum_ii" or "lc_167"
    leetcode_id             INTEGER,
    title                   TEXT NOT NULL,
    difficulty              TEXT NOT NULL,      -- Easy | Medium | Hard
    primary_pattern         TEXT NOT NULL,
    subpattern              TEXT NOT NULL,
    secondary_patterns      TEXT NOT NULL DEFAULT '[]',  -- JSON array
    prerequisites           TEXT NOT NULL DEFAULT '[]',  -- JSON array
    time_complexity_target  TEXT,
    space_complexity_target TEXT,
    educational_utility     TEXT,
    official_link           TEXT,
    provenance              TEXT NOT NULL,      -- user_repo | curated_core | eval_dataset
    verification_status     TEXT NOT NULL DEFAULT 'planned',
    previously_solved       INTEGER NOT NULL DEFAULT 0,  -- boolean
    created_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Attempt: one per code submission -------------------------------------------
CREATE TABLE IF NOT EXISTS attempts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id      TEXT NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    session_id      INTEGER REFERENCES practice_sessions(id),
    submitted_code  TEXT NOT NULL,
    overall_verdict TEXT NOT NULL,   -- AC | WA | TLE | COMPILATION_ERROR | RUNTIME_ERROR
    passed_tests    INTEGER NOT NULL DEFAULT 0,
    total_tests     INTEGER NOT NULL DEFAULT 0,
    compile_ms      REAL,            -- compilation wall-clock time in ms
    run_ms          REAL,            -- total test execution time in ms
    compiler_stderr TEXT,
    submitted_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Per test-case verdicts within an attempt -----------------------------------
CREATE TABLE IF NOT EXISTS test_results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id  INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    test_index  INTEGER NOT NULL,
    verdict     TEXT NOT NULL,
    input_data  TEXT,
    expected    TEXT,
    actual      TEXT,
    stderr      TEXT
);

-- Hints unlocked during an attempt session -----------------------------------
CREATE TABLE IF NOT EXISTS hints_accessed (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id  INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    hint_level  INTEGER NOT NULL CHECK (hint_level BETWEEN 1 AND 5),
    accessed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Mistake diagnoses produced by the tutor -----------------------------------
CREATE TABLE IF NOT EXISTS diagnoses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id      INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    mistake_category TEXT NOT NULL,
    tutor_question  TEXT NOT NULL,
    raw_response    TEXT,
    latency_ms      REAL,
    diagnosed_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id TEXT NOT NULL REFERENCES problems(id),
    started_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS session_hints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES practice_sessions(id),
    hint_level INTEGER NOT NULL CHECK (hint_level BETWEEN 1 AND 5),
    accessed_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS problem_aliases (
    alias_id TEXT PRIMARY KEY,
    problem_id TEXT NOT NULL REFERENCES problems(id),
    legacy_metadata TEXT
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Open a WAL-mode, foreign-key-enabled SQLite connection."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Path) -> sqlite3.Connection:
    """Create all tables if they do not exist. Returns an open connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(db_path)
    conn.executescript(DDL)
    # Additive migration: retain all v1 tables and every existing learning record.
    with conn:
        columns = {r[1] for r in conn.execute('PRAGMA table_info(attempts)')}
        if 'session_id' not in columns:
            conn.execute('ALTER TABLE attempts ADD COLUMN session_id INTEGER REFERENCES practice_sessions(id)')
        conn.execute('INSERT OR IGNORE INTO schema_version(version) VALUES (2)')
    return conn
