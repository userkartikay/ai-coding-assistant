import asyncio
import json
import time
import pytest
import httpx
from fastapi.testclient import TestClient
from backend.api.app import create_app
from backend.api.references import fingerprint
from backend.core.schemas import ProgressiveHintResponse
from backend.eval.dataset import EVALUATION_DATASET
from backend.curriculum.registry import get_registry


class FakeTutor:
    def __init__(self, fail_at=None):
        self.calls = []
        self.fail_at = fail_at

    async def check_health(self): return True

    async def get_progressive_hint(self, **kw):
        level = kw['level'].value
        self.calls.append(level)
        if level == self.fail_at: raise ValueError('failed generation')
        data = dict(level=level, title='Guidance', guidance='Observe the input properties.',
                    guiding_question='Which property matters here?' if level < 4 else None, contains_code=level >= 4)
        if level == 4: data['pseudocode'] = 'REPEAT until the boundary condition holds'
        if level == 5: data.update(code='int solution() { return 0; }', explanation='Explain the invariant.', time_complexity='O(N)', space_complexity='O(1)')
        return ProgressiveHintResponse.model_validate(data)


@pytest.fixture
def client():
    with TestClient(create_app(tutor_factory=FakeTutor), base_url='http://127.0.0.1') as client:
        yield client


def headers(client): return {'X-Mentor-Token': client.get('/api/bootstrap').json()['token']}


def start(client, problem='lc_167'):
    response = client.post('/api/sessions', json={'problem_id': problem}, headers=headers(client))
    assert response.status_code == 200
    return response.json()['id']


def test_catalogue_fidelity_and_missing_content(client):
    questions = client.get('/api/problems').json()
    assert len(questions) == 133 and sum(p['executable'] for p in questions) == 10
    assert len({p['id'] for p in questions}) == 133
    for item in get_registry():
        detail = client.get(f'/api/problems/{item.id}').json()
        assert detail['metadata'] == item.metadata.model_dump(mode='json')
        assert 'canonical_solution' not in json.dumps(detail)
        if item.is_executable:
            assert detail['description'] == item.execution.description
            assert detail['function_signature'] == item.execution.function_signature
        else:
            from backend.curriculum.content import SUMMARIES
            assert detail['description'] == SUMMARIES.get(item.metadata.leetcode_id) and detail['constraints'] is None
            assert detail['starter_code'] == '' and detail['examples'] == []


def test_local_authentication_and_origin_boundaries(client):
    assert client.post('/api/sessions', json={'problem_id':'lc_167'}).status_code == 403
    assert client.post('/api/sessions', json={'problem_id':'lc_167'}, headers={**headers(client),'Origin':'https://attacker.example'}).status_code == 403
    assert client.post('/api/sessions', json={'problem_id':'lc_167'}, headers={**headers(client),'Origin':'http://127.0.0.1:5173'}).status_code == 200
    assert client.get('/api/problems',headers={'Host':'attacker.example'}).status_code == 400


def test_no_code_execution_endpoints_or_browser_source_accepted(client,monkeypatch):
    from backend.runner.cpp_runner import CppRunner
    def prohibited(*args,**kw): raise AssertionError('HTTP must never execute source')
    monkeypatch.setattr(CppRunner,'run_test_suite',prohibited)
    for path in ('/api/execute','/api/run','/api/judge'):
        assert client.post(path,json={'code':'int main(){}','trusted':True},headers=headers(client)).status_code == 404
    assert client.post('/api/sessions',json={'problem_id':'lc_167','code':'int main(){}'},headers=headers(client)).status_code == 422
    assert client.get('/api/problems/lc_167/mock-results').json()['student_code_executed'] is False
    assert client.get('/api/problems/lc_167/reference-results').status_code == 200


def test_server_hint_gate_and_cache(client):
    sid = start(client)
    path = f'/api/sessions/{sid}/hints'
    assert client.post(path,json={'level':5},headers=headers(client)).status_code == 409
    for level in range(1,6):
        response=client.post(path,json={'level':level},headers=headers(client))
        assert response.status_code == 200 and response.json()['unlocked_level'] == level
    response=client.post(path,json={'level':1},headers=headers(client))
    assert response.json()['unlocked_level']==5
    assert client.app.state.sessions[sid].app.tutor.calls == [1,2,3,4,5]


@pytest.mark.parametrize('fail_at',[1,2])
def test_failed_generation_never_unlocks(client,fail_at):
    sid=start(client);entry=client.app.state.sessions[sid];entry.app.tutor.fail_at=fail_at
    if fail_at==2: assert client.post(f'/api/sessions/{sid}/hints',json={'level':1},headers=headers(client)).status_code==200
    response=client.post(f'/api/sessions/{sid}/hints',json={'level':fail_at},headers=headers(client))
    assert response.status_code==503
    state=client.get(f'/api/sessions/{sid}',headers=headers(client)).json()
    assert state['unlocked_level']==fail_at-1 and str(fail_at) not in state['hints']


def test_catalogue_only_sessions_are_unavailable(client):
    p=next(p for p in get_registry() if not p.is_executable)
    assert client.post('/api/sessions',json={'problem_id':p.id},headers=headers(client)).status_code==409


def test_session_expiry_and_bounded_capacity(client):
    sid=start(client);client.app.state.sessions[sid].touched=time.monotonic()-7201
    assert client.get(f'/api/sessions/{sid}',headers=headers(client)).status_code==410
    sid=start(client);entry=client.app.state.sessions[sid]
    for i in range(100):client.app.state.sessions[str(i)]=entry
    assert client.post('/api/sessions',json={'problem_id':'lc_167'},headers=headers(client)).status_code==429


@pytest.mark.parametrize('scenario',['AC','WA','COMPILATION_ERROR','TLE','RUNTIME_ERROR'])
def test_mock_reports_are_explicitly_mock(client,scenario):
    payload=client.get(f'/api/problems/lc_167/mock-results?scenario={scenario}').json()
    assert payload['source']=='mock' and payload['student_code_executed'] is False
    assert payload['report']['overall_verdict']==scenario


def test_reference_fingerprint_rejects_stale_report(tmp_path):
    path=tmp_path/'bad.json';path.write_text(json.dumps({'recorded_at':'now','problems':{'lc_167':{'fingerprint':'stale','reports':{}}}}))
    with TestClient(create_app(FakeTutor,path), base_url='http://127.0.0.1') as c:
        assert c.get('/api/problems/lc_167/reference-results').status_code==404


@pytest.mark.asyncio
async def test_local_model_calls_are_serialized():
    entered=asyncio.Event();release=asyncio.Event()
    class WaitingTutor(FakeTutor):
        async def get_progressive_hint(self,**kw):
            entered.set();await release.wait();return await super().get_progressive_hint(**kw)
    app=create_app(WaitingTutor)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1') as c:
        h={'X-Mentor-Token':(await c.get('/api/bootstrap')).json()['token']}
        first=(await c.post('/api/sessions',json={'problem_id':'lc_167'},headers=h)).json()['id']
        second=(await c.post('/api/sessions',json={'problem_id':'lc_70'},headers=h)).json()['id']
        pending=asyncio.create_task(c.post(f'/api/sessions/{first}/hints',json={'level':1},headers=h))
        await entered.wait()
        assert (await c.post(f'/api/sessions/{second}/hints',json={'level':1},headers=h)).status_code==409
        release.set();assert (await pending).status_code==200
