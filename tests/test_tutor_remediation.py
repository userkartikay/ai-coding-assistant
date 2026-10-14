import json
import pytest
import httpx
from backend.core.ollama_client import OllamaClient
from backend.core.schemas import HintLevel, ProgressiveHintResponse
from backend.cli.interactive_cli import SocraticCliApp


def payload(level):
    data={'level':level,'title':'Guidance','guidance':'Consider the relationship between the input values.',
          'guiding_question':'Which property helps avoid repeated work?' if level<4 else None,
          'contains_code':level>=4}
    if level==4:data['pseudocode']='SET left to first index\nREPEAT until boundaries meet\n  compare candidate total\n  move the appropriate boundary'
    if level==5:data.update(code='vector<int> twoSum(vector<int>& a, int target) { return {}; }',
        explanation='Compare a candidate sum with the target and discard impossible pairs.',
        time_complexity='O(N)',space_complexity='O(1)')
    return data


@pytest.mark.parametrize('level',range(1,6))
def test_all_hint_tiers_have_distinct_requirements(level):
    assert ProgressiveHintResponse.model_validate(payload(level)).level.value==level
    bad=payload(level)
    if level<4:bad['guiding_question']=None
    elif level==4:bad['pseudocode']=None
    else:bad['space_complexity']=None
    with pytest.raises(ValueError):ProgressiveHintResponse.model_validate(bad)


@pytest.mark.parametrize('text',['int answer = 42; return answer;', 'Use two pointers.', 'Apply binary search.'])
def test_obvious_level_one_leakage_rejected(text):
    data=payload(1);data['guidance']=text
    with pytest.raises(ValueError):ProgressiveHintResponse.model_validate(data)


def test_level_two_cannot_give_conditional_pointer_update_rules():
    data=payload(2)
    data['guidance']='If the sum is less than the target, move the left pointer right; otherwise move the right pointer left.'
    with pytest.raises(ValueError,match='conditional update rules'):
        ProgressiveHintResponse.model_validate(data)


class Responses(OllamaClient):
    def __init__(self, responses):super().__init__();self.responses=iter(responses);self.calls=[]
    async def generate_raw(self,**kwargs):
        self.calls.append(kwargs)
        value=next(self.responses)
        if isinstance(value,Exception):raise value
        return value


@pytest.mark.asyncio
@pytest.mark.parametrize('bad', [('{"level":4,',{'done':True}),
    (json.dumps(payload(4)),{'done':True,'done_reason':'length'}),
    ('',{'done':True,'thinking':'private reasoning'}),
    (json.dumps(payload(5)),{'done':True}),
    httpx.ReadTimeout('timeout')])
async def test_bounded_recovery_for_invalid_response(bad):
    client=Responses([bad,(json.dumps(payload(4)),{'done':True,'done_reason':'stop'})])
    result=await client.get_progressive_hint(HintLevel(4),'P','D','C')
    assert result.level.value==4 and len(client.calls)==2
    assert isinstance(client.calls[0]['response_schema'],dict)
    assert client.calls[0]['think'] is False
    assert client.calls[1]['num_predict']>client.calls[0]['num_predict']


@pytest.mark.asyncio
async def test_recovery_stops_after_two_calls():
    client=Responses([('garbage',{'done':True})]*2)
    with pytest.raises(ValueError,match='two bounded attempts'):
        await client.get_progressive_hint(HintLevel(5),'P','D','C')
    assert len(client.calls)==2


@pytest.mark.asyncio
async def test_no_silent_context_truncation():
    client=Responses([])
    with pytest.raises(ValueError,match='context is too large'):
        await client.diagnose_mistake('P','D','O(N)','x'*10000,'test failure')
    assert not client.calls


@pytest.mark.asyncio
async def test_sequential_unlock_after_valid_generation_only():
    class Tutor:
        async def get_progressive_hint(self,**kw):return ProgressiveHintResponse.model_validate(payload(kw['level'].value))
    app=SocraticCliApp(tutor=Tutor());app.select_problem(0)
    for level in range(1,6):
        response=await app.request_progressive_hint(level)
        assert response.level.value==level and app.unlocked_hint_level==level
    app.select_problem(1)
    assert app.unlocked_hint_level==0


@pytest.mark.asyncio
async def test_provider_wrong_level_cannot_unlock():
    class Tutor:
        async def get_progressive_hint(self,**kw):return ProgressiveHintResponse.model_validate(payload(5))
    app=SocraticCliApp(tutor=Tutor());app.select_problem(0)
    await app.request_progressive_hint(1)
    assert app.unlocked_hint_level==0


@pytest.mark.asyncio
async def test_cli_pre_submission_hint_session(tmp_path):
    from scripts.seed_db import seed
    from backend.db.schema import initialize_database
    from backend.db.repository import get_session_hints
    class Tutor:
        async def get_progressive_hint(self,**kw):return ProgressiveHintResponse.model_validate(payload(1))
    path=tmp_path/'mentor.db';seed(path);conn=initialize_database(path)
    app=SocraticCliApp(tutor=Tutor(),connection=conn);app.select_problem(0)
    await app.request_progressive_hint(1)
    assert get_session_hints(conn,app.session_id)==[1]
    assert conn.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]==0
    conn.close()
