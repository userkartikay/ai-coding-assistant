#!/usr/bin/env python3
"""Seed the SQLite database with the curated curriculum catalogue and evaluation dataset.

Usage:
    python scripts/seed_db.py                      # default: data/mentor.db
    python scripts/seed_db.py --db path/to/db.db

This script is idempotent: running it multiple times preserves all learning history (ON CONFLICT DO UPDATE).
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.schema import initialize_database
from backend.db.repository import upsert_problem, atomic_write
from backend.curriculum.catalogue import CURATED_CATALOGUE
from backend.eval.dataset import EVALUATION_DATASET
from backend.curriculum.registry import get_registry
from backend.curriculum.identity import LEGACY_IDS, stable_id


def _problem_row_from_curriculum(p) -> dict:
    """Convert a CurriculumProblem into a flat dict for the problems table."""
    # Derive a slug ID from title or leetcode_id
    slug = f"lc_{p.leetcode_id}" if p.leetcode_id else p.title.lower().replace(" ", "_")
    return {
        "id": slug,
        "leetcode_id": p.leetcode_id,
        "title": p.title,
        "difficulty": p.difficulty.value,
        "primary_pattern": p.primary_pattern,
        "subpattern": p.subpattern,
        "secondary_patterns": json.dumps(p.secondary_patterns),
        "prerequisites": json.dumps(p.prerequisites),
        "time_complexity_target": p.time_complexity_target,
        "space_complexity_target": p.space_complexity_target,
        "educational_utility": p.educational_utility,
        "official_link": p.official_link,
        "provenance": p.provenance.value,
        "verification_status": p.verification_status.value,
        "previously_solved": int(p.previously_solved_by_user),
    }


@atomic_write
def seed_connection(conn) -> None:
    """Atomic metadata seed and legacy-ID consolidation. No history is discarded."""
    for item in get_registry():
        row = _problem_row_from_curriculum(item.metadata)
        row['verification_status'] = 'verified' if item.is_executable else 'planned'
        upsert_problem(conn, row)
    for legacy, number in LEGACY_IDS.items():
        target = stable_id(number)
        old = conn.execute('SELECT * FROM problems WHERE id=?', (legacy,)).fetchone()
        conn.execute('INSERT INTO problem_aliases(alias_id,problem_id,legacy_metadata) VALUES (?,?,?) '
                     'ON CONFLICT(alias_id) DO UPDATE SET problem_id=excluded.problem_id, '
                     'legacy_metadata=COALESCE(problem_aliases.legacy_metadata,excluded.legacy_metadata)',
                     (legacy, target, json.dumps(dict(old)) if old else None))
        if old:
            conn.execute('UPDATE problems SET previously_solved=MAX(previously_solved,?) WHERE id=?',
                         (old['previously_solved'], target))
            conn.execute('UPDATE attempts SET problem_id=? WHERE problem_id=?', (target, legacy))
            conn.execute('UPDATE practice_sessions SET problem_id=? WHERE problem_id=?', (target, legacy))
            # Dependencies now reference the stable row. Preserve the old metadata above.
            conn.execute('DELETE FROM problems WHERE id=?', (legacy,))
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS unique_leetcode_problem ON problems(leetcode_id)')
    conn.execute('INSERT OR IGNORE INTO schema_version(version) VALUES (3)')


def seed(db_path: Path) -> None:
    print(f'[seed_db] Initializing database at: {db_path}')
    conn = initialize_database(db_path)
    try:
        seed_connection(conn)
        count = conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0]
        print(f'[seed_db] {count} unique problems; learning history preserved.')
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed the mentor SQLite database.")
    parser.add_argument(
        "--db",
        default="data/mentor.db",
        help="Path to the SQLite database file (default: data/mentor.db)",
    )
    args = parser.parse_args()
    seed(Path(args.db))


if __name__ == "__main__":
    main()
