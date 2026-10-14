import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from backend.curriculum.catalogue import CURATED_CATALOGUE, ORIGINAL_CATALOGUE
from backend.curriculum.registry import get_registry
from backend.curriculum.lessons import get_lessons
from backend.curriculum.source_identity import SourceIdentity
from backend.db.schema import initialize_database
from backend.db.repository import save_attempt, record_hint_access, save_diagnosis, create_practice_session, record_session_hint
from tests.test_persistence_remediation import failed_report
from scripts.seed_db import seed_connection

def test_all_official_mappings_and_unique_numbers():
    official=json.loads(Path('docs/LEETCODE_IDENTITIES.json').read_text(encoding='utf-8'))
    expected={p['leetcode_id']:p for p in official['problems']}
    assert len(CURATED_CATALOGUE)==133
    assert len(expected)==len(CURATED_CATALOGUE)
    assert len({p.leetcode_id for p in CURATED_CATALOGUE})==133
    for p in get_registry():
        m=p.metadata; source=expected[m.leetcode_id]
        assert p.id==f'lc_{m.leetcode_id}'
        assert (m.title,m.official_link,m.difficulty.value)==(source['title'],source['official_link'],source['difficulty'])
    assert expected[167]['title']=='Two Sum II - Input Array Is Sorted'
    assert expected[1]['title']=='Two Sum'
    assert expected[200]['official_link']=='https://leetcode.com/problems/number-of-islands/'

def test_original_53_records_exactly_preserved():
    old=json.loads(Path('docs/original-catalogue-53.json').read_text(encoding='utf-8'))
    assert len(old)==len(ORIGINAL_CATALOGUE)==53
    assert [p.model_dump(mode='json') for p in CURATED_CATALOGUE[:53]]==old
    assert sum(p.is_executable for p in get_registry())==10
    assert all(not p.is_executable for p in get_registry()[53:])

def test_duplicate_official_identity_rejected_before_registry_or_seed(monkeypatch):
    import backend.curriculum.registry as registry
    monkeypatch.setattr(registry,'CURATED_CATALOGUE',CURATED_CATALOGUE+[CURATED_CATALOGUE[0]])
    with pytest.raises(ValueError):registry.get_registry()

def test_expansion_reseed_preserves_ids_history_and_pre_submission_hints(tmp_path, monkeypatch):
    import backend.curriculum.registry as registry
    conn=initialize_database(tmp_path/'history.db')
    with monkeypatch.context() as patch:
        patch.setattr(registry,'CURATED_CATALOGUE',list(ORIGINAL_CATALOGUE))
        seed_connection(conn)
    assert conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0]==53
    session=create_practice_session(conn,'lc_167'); record_session_hint(conn,session,1)
    attempt=save_attempt(conn,'lc_167','unchanged student draft',failed_report(),session_id=session)
    record_hint_access(conn,attempt,2);save_diagnosis(conn,attempt,'other','Preserved question?')
    tables=['attempts','test_results','hints_accessed','diagnoses','practice_sessions','session_hints']
    before={table:[tuple(r) for r in conn.execute(f'SELECT * FROM {table}')] for table in tables}
    seed_connection(conn);seed_connection(conn)
    assert conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0]==133
    assert {table:[tuple(r) for r in conn.execute(f'SELECT * FROM {table}')] for table in tables}==before
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()

def test_lesson_topics_subpatterns_links_and_diagram_indices():
    lessons=get_lessons(); registry={p.metadata.leetcode_id:p for p in get_registry()}
    assert len(lessons)==16
    assert len({l.id for l in lessons})==16
    for p in get_registry():
        assert sum(p.metadata.primary_pattern in l.patterns for l in lessons)==1
        assert p.metadata.subpattern.strip()
    for l in lessons:
        assert l.stl and l.template and l.complexity and l.recognition_questions and l.misconceptions
        assert len({s.name for s in l.subpatterns})==len(l.subpatterns)
        assert len(set(l.related_questions))==len(l.related_questions)
        assert all(registry[n].metadata.primary_pattern in l.patterns for n in l.related_questions)
        for step in l.walkthrough:
            assert all(0<=i<len(step.values) for i in step.active)
            assert all(0<=a<len(step.values) and 0<=b<len(step.values) for a,b in step.links)

@pytest.mark.parametrize('payload',[
    {'source':'local','source_id':'my-question','leetcode_id':1},
    {'source':'leetcode','source_id':'fake'},
    {'source':'leetcode','source_id':'2','leetcode_id':1},
])
def test_non_leetcode_source_cannot_invent_numbers(payload):
    with pytest.raises(ValidationError): SourceIdentity.model_validate(payload)

def test_source_specific_identity_contract():
    assert SourceIdentity(source='local',source_id='my-question').leetcode_id is None
    assert SourceIdentity(source='leetcode',source_id='167',leetcode_id=167).source_id=='167'

def test_cli_uses_official_number_in_problem_title():
    from backend.cli.interactive_cli import SocraticCliApp
    app=SocraticCliApp();app.select_problem(0)
    p=app.active_problem
    assert f'PROBLEM: #{p.leetcode_id} — {p.title}' in app.format_problem_display()
