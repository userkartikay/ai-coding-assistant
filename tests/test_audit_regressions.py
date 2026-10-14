"""Concrete independent-audit reproductions; no live model required."""
import sqlite3
import pytest
from backend.db.schema import DDL
from backend.db.repository import (upsert_problem, save_attempt, record_hint_access,
                                   save_diagnosis, get_attempts_for_problem)
from scripts.seed_db import _problem_row_from_curriculum, seed
from backend.curriculum.catalogue import CURATED_CATALOGUE
from backend.core.schemas import ProgressiveHintResponse, HintLevel
from backend.core.ollama_client import OllamaClient
from backend.cli.interactive_cli import SocraticCliApp
from backend.eval.dataset import EVALUATION_DATASET
from backend.runner.schemas import ExecutionReport, TestVerdict


@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    yield conn
    conn.close()


def report():
    return ExecutionReport(overall_verdict=TestVerdict.COMPILATION_ERROR,
                           compilation_success=False, total_tests=1)


def test_upsert_preserves_learning_history(db):
    p = _problem_row_from_curriculum(CURATED_CATALOGUE[0])
    upsert_problem(db, p)
    a = save_attempt(db, p['id'], 'code', report())
    record_hint_access(db, a, 1)
    save_diagnosis(db, a, 'other', 'Question?')
    upsert_problem(db, {**p, 'title': 'Updated title'})
    for table in ('attempts', 'hints_accessed', 'diagnoses'):
        assert db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 1


def test_same_second_attempts_newest_first(db):
    p = _problem_row_from_curriculum(CURATED_CATALOGUE[0]); upsert_problem(db, p)
    ids = [save_attempt(db, p['id'], str(i), report()) for i in range(2)]
    db.execute("UPDATE attempts SET submitted_at='2026-10-12 00:00:00'"); db.commit()
    assert [r['id'] for r in get_attempts_for_problem(db, p['id'])] == ids[::-1]


def test_seed_has_one_identity_per_leetcode_problem(tmp_path):
    path = tmp_path / 'seed.db'; seed(path)
    with sqlite3.connect(path) as c:
        assert c.execute('SELECT COUNT(*) FROM problems').fetchone()[0] == 133
        assert c.execute('SELECT COUNT(*) FROM problems WHERE leetcode_id IS NULL').fetchone()[0] == 0


@pytest.mark.parametrize('payload', [
    {'level': 1, 'title': 'Nudge', 'guidance': 'int main(){return 0;}', 'contains_code': True},
    {'level': 1, 'title': 'Nudge', 'guidance': 'Think about bounds.', 'contains_code': False},
    {'level': 2, 'title': '', 'guidance': '', 'guiding_question': '?', 'contains_code': False},
])
def test_invalid_hint_tiers_rejected(payload):
    with pytest.raises(ValueError):
        ProgressiveHintResponse.model_validate(payload)


class Offline:
    async def get_progressive_hint(self, **kwargs):
        raise RuntimeError('offline')


@pytest.mark.asyncio
async def test_failed_hint_does_not_unlock_or_reveal_pattern():
    app = SocraticCliApp(tutor=Offline()); app.select_problem(0)
    h = await app.request_progressive_hint(1)
    assert 'two pointers' not in h.guidance.lower()
    assert app.unlocked_hint_level == 0


@pytest.mark.asyncio
async def test_hint_cannot_skip_to_solution():
    app = SocraticCliApp(tutor=Offline()); app.select_problem(0)
    with pytest.raises(ValueError):
        await app.request_progressive_hint(5)


def test_problem_display_does_not_disclose_pattern():
    app = SocraticCliApp(); app.select_problem(0)
    assert 'Pattern:' not in app.format_problem_display()


def test_islands_required_signature_not_helper():
    app = SocraticCliApp(); app.select_problem(6)
    signature = app.format_problem_display().split('EXPECTED FUNCTION SIGNATURE')[1]
    assert 'int numIslands' in signature
    assert 'void dfs' not in signature


@pytest.mark.asyncio
async def test_wrong_requested_level_is_rejected():
    class WrongLevel(OllamaClient):
        async def generate_raw(self, **kwargs):
            return '{"level":5,"title":"Solution","guidance":"int main(){return 0;} Time O(1), Space O(1). Explanation.","contains_code":true}', {'done': True}
    with pytest.raises(ValueError):
        await WrongLevel().get_progressive_hint(HintLevel.LEVEL_1_NUDGE, 'P', 'D', 'C')
