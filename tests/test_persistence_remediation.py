import json
import sqlite3
import pytest
from backend.db.schema import DDL, initialize_database
from backend.db.repository import (upsert_problem, save_attempt, record_hint_access,
    save_diagnosis, create_practice_session, record_session_hint, get_session_hints, get_problem)
from backend.runner.schemas import ExecutionReport, TestCaseResult, TestVerdict
from backend.curriculum.catalogue import CURATED_CATALOGUE
from backend.curriculum.registry import get_registry
from scripts.seed_db import seed, seed_connection, _problem_row_from_curriculum


def failed_report():
    return ExecutionReport(overall_verdict=TestVerdict.WA, compilation_success=True,
        total_tests=1, test_results=[TestCaseResult(test_case_id='edge', passed=False,
        verdict=TestVerdict.WA, actual_output='0', expected_output='1')])


def test_reseed_preserves_attempt_results_hints_diagnoses(tmp_path):
    path = tmp_path/'mentor.db'; seed(path)
    conn = initialize_database(path)
    attempt = save_attempt(conn, 'lc_167', 'my code', failed_report())
    record_hint_access(conn, attempt, 1); save_diagnosis(conn, attempt, 'other', 'Question?')
    conn.close(); seed(path); seed(path)
    conn = initialize_database(path)
    for table in ('attempts','test_results','hints_accessed','diagnoses'):
        assert conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 1
    assert conn.execute('SELECT submitted_code FROM attempts').fetchone()[0] == 'my code'
    assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
    conn.execute("UPDATE problems SET previously_solved=1 WHERE id='lc_70'")
    conn.commit()
    seed_connection(conn)
    assert get_problem(conn, 'lc_70')['previously_solved'] == 1
    conn.close()


def test_v1_duplicate_migration_preserves_history_and_original_metadata(tmp_path):
    path = tmp_path/'legacy.db'
    old_ddl = DDL[:DDL.index('CREATE TABLE IF NOT EXISTS practice_sessions')].replace(
        '    session_id      INTEGER REFERENCES practice_sessions(id),\n', '')
    conn = sqlite3.connect(path); conn.row_factory=sqlite3.Row; conn.executescript(old_ddl)
    old = _problem_row_from_curriculum(CURATED_CATALOGUE[0])
    old.update(id='two_sum_ii', leetcode_id=None, difficulty='Medium', provenance='eval_dataset')
    keys = list(old)
    conn.execute(f"INSERT INTO problems ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", tuple(old.values()))
    attempt = conn.execute("INSERT INTO attempts(problem_id,submitted_code,overall_verdict) VALUES ('two_sum_ii','legacy code','WA')").lastrowid
    conn.execute("INSERT INTO test_results(attempt_id,test_index,verdict,actual) VALUES (?,0,'WA','0')",(attempt,))
    conn.execute('INSERT INTO hints_accessed(attempt_id,hint_level) VALUES (?,2)', (attempt,))
    conn.execute("INSERT INTO diagnoses(attempt_id,mistake_category,tutor_question) VALUES (?,'other','old question')",(attempt,))
    conn.commit();conn.close()
    seed(path);seed(path)
    conn=initialize_database(path)
    assert conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0] == 133
    assert conn.execute('SELECT problem_id,submitted_code FROM attempts').fetchone()[:] == ('lc_167','legacy code')
    for table in ('test_results','hints_accessed','diagnoses'):
        assert conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 1
    archived=json.loads(conn.execute("SELECT legacy_metadata FROM problem_aliases WHERE alias_id='two_sum_ii'").fetchone()[0])
    assert archived['provenance']=='eval_dataset'
    assert get_problem(conn,'two_sum_ii')['id']=='lc_167'
    assert get_problem(conn,'lc_167')['difficulty']==CURATED_CATALOGUE[0].difficulty.value
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()


def test_pre_submission_session_hints_and_session_validation(tmp_path):
    path=tmp_path/'mentor.db';seed(path);conn=initialize_database(path)
    session=create_practice_session(conn,'lc_167')
    record_session_hint(conn,session,1)
    assert conn.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]==0
    assert get_session_hints(conn,session)==[1]
    attempt=save_attempt(conn,'lc_167','code',failed_report(),session_id=session)
    assert conn.execute('SELECT session_id FROM attempts WHERE id=?',(attempt,)).fetchone()[0]==session
    with pytest.raises(ValueError):save_attempt(conn,'lc_70','bad',failed_report(),session_id=session)
    with pytest.raises(sqlite3.IntegrityError):record_session_hint(conn,session,6)
    assert get_session_hints(conn,session)==[1]
    conn.close()


def test_attempt_rollback_on_child_insert_failure(tmp_path):
    path=tmp_path/'mentor.db';seed(path);conn=initialize_database(path)
    conn.execute("CREATE TRIGGER fail_result BEFORE INSERT ON test_results BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(sqlite3.IntegrityError):save_attempt(conn,'lc_167','code',failed_report())
    # A subsequent successful write must not commit a partial attempt.
    create_practice_session(conn,'lc_167')
    assert conn.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]==0
    conn.close()


def test_seed_rollback_on_mid_seed_failure(tmp_path,monkeypatch):
    import scripts.seed_db as module
    conn=initialize_database(tmp_path/'empty.db');original=module.upsert_problem;calls=[]
    def fail_second(c,p):
        calls.append(p['id'])
        if len(calls)==2:raise RuntimeError('injected')
        return original(c,p)
    monkeypatch.setattr(module,'upsert_problem',fail_second)
    with pytest.raises(RuntimeError):seed_connection(conn)
    assert conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0]==0
    conn.close()


def test_registry_preserves_metadata_and_distinguishes_executability():
    registry=get_registry()
    assert len(registry)==133
    assert sum(p.is_executable for p in registry)==10
    assert [p.metadata for p in registry]==CURATED_CATALOGUE
    assert len({p.id for p in registry})==133
    assert all(p.execution.function_signature for p in registry if p.is_executable)
