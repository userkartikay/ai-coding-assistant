import json
import httpx
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from backend.api.app import create_app
from backend.core.learning import SolutionReview, LessonAnswer
from backend.core.ollama_client import OllamaClient
from backend.curriculum.registry import get_registry
from backend.curriculum.lessons import get_lessons
from tests.test_frontend_api import FakeTutor, headers, start

def feedback(mode='approach'):
    result=dict(mode=mode,evidence='not_executed',identified_pattern='Sorted pair scan',
        invariant='Remaining candidates lie between the two boundary positions.',
        estimated_time='O(N) if each position moves only inward',estimated_space='O(1) auxiliary',
        observations=['Both positions moving together may skip valid pairs.'],
        edge_cases=['Check a valid pair next to the left endpoint.'],
        simplification='Keep only the boundary positions and current sum.',
        uncertainty='No source execution or test evidence is available; this is static analysis.',
        guiding_question='Which pairs are eliminated when both boundaries move?',alternatives=[])
    if mode=='compare':
        result['alternatives']=[dict(name='Hash lookup',direction='Remember earlier complements while scanning entries.',
            estimated_time='O(N) expected',estimated_space='O(N)',tradeoff='Additional memory preserves original order.'),
            dict(name='Per-element search',direction='Search the sorted suffix for each missing complement.',
            estimated_time='O(N log N)',estimated_space='O(1)',tradeoff='Less memory than hashing, but repeated logarithmic searches.')]
    return result

def lesson_feedback(id='binary-search'):
    return dict(lesson_id=id,answer='The half-open boundary can equal the array size, so check it before reading.',
        material_sections=['template','misconceptions'],uncertainty='This explanation assumes sorted input.',
        guiding_question='What does the returned position mean when the target is larger than every entry?')

class LearningTutor(FakeTutor):
    async def review_solution(self,problem,code,mode): return feedback(mode)
    async def answer_lesson_question(self,lesson,question): return lesson_feedback(lesson.id)

def test_review_requires_explicit_optin_and_never_executes_or_unlocks(monkeypatch):
    from backend.runner.cpp_runner import CppRunner
    def prohibited(*args,**kwargs): raise AssertionError('Do not execute review source')
    monkeypatch.setattr(CppRunner,'run_test_suite',prohibited)
    with TestClient(create_app(tutor_factory=LearningTutor),base_url='http://127.0.0.1') as c:
        sid=start(c);body=dict(problem_id='lc_167',code='vector<int> solve() { return {}; }',mode='approach')
        assert c.post('/api/reviews',json=body,headers=headers(c)).status_code==422
        body['reveal_teaching_details']=True
        assert c.post('/api/reviews',json=body).status_code==403
        response=c.post('/api/reviews',json=body,headers=headers(c))
        assert response.status_code==200
        data=response.json();assert data['source']=='ai_review' and data['student_code_executed'] is False
        assert data['feedback']['evidence']=='not_executed' and 'overall_verdict' not in data['feedback']
        assert c.get(f'/api/sessions/{sid}',headers=headers(c)).json()['unlocked_level']==0
        body['mode']='compare'
        assert len(c.post('/api/reviews',json=body,headers=headers(c)).json()['feedback']['alternatives'])==2
        body['trusted']=True
        assert c.post('/api/reviews',json=body,headers=headers(c)).status_code==422
        body.pop('trusted');body['problem_id']='lc_1'
        assert c.post('/api/reviews',json=body,headers=headers(c)).status_code==409

def test_lesson_api_grounding_links_and_auth():
    with TestClient(create_app(tutor_factory=LearningTutor),base_url='http://127.0.0.1') as c:
        lessons=c.get('/api/lessons').json();assert len(lessons)==16
        for l in lessons:
            for n in l['related_questions']:
                detail=c.get(f'/api/problems/lc_{n}').json();assert detail['metadata']['leetcode_id']==n
        path='/api/lessons/binary-search/questions'
        assert c.post(path,json={'question':'Why check bounds?'}).status_code==403
        result=c.post(path,json={'question':'Why check bounds?'},headers=headers(c))
        assert result.status_code==200 and result.json()['source']=='ai_lesson'
        assert result.json()['feedback']['lesson_id']=='binary-search'
        assert c.post('/api/lessons/fake/questions',json={'question':'Why check bounds?'},headers=headers(c)).status_code==404

@pytest.mark.parametrize('change',[
    {'evidence':'passed'}, {'invariant':''}, {'observations':['']}, {'uncertainty':'sure'},
    {'invariant':'The solution is AC.'}, {'simplification':'int solution() { return 0; }'},
    {'overall_verdict':'AC'}, {'mode':'compare'}, {'uncertainty':'None regarding correctness of this solution.'},
])
def test_invalid_review_outputs_rejected(change):
    with pytest.raises(ValidationError):SolutionReview.model_validate({**feedback(),**change})

def test_compare_distinct_alternatives_required():
    data=feedback('compare');data['alternatives'][1]['name']=data['alternatives'][0]['name']
    with pytest.raises(ValidationError):SolutionReview.model_validate(data)
    assert len(SolutionReview.model_validate(feedback('compare')).alternatives)==2

@pytest.mark.asyncio
@pytest.mark.parametrize('failure',['malformed','truncated','timeout','mode'])
async def test_review_bounded_recovery(failure,monkeypatch):
    client=OllamaClient();calls=[]; p=next(p for p in get_registry() if p.id=='lc_167')
    async def raw(**kwargs):
        calls.append(kwargs)
        if len(calls)==1:
            if failure=='timeout':raise httpx.ReadTimeout('timeout')
            if failure=='mode':return json.dumps(feedback('compare')),{'done':True}
            return ('not json' if failure=='malformed' else json.dumps(feedback())),{'done':failure!='truncated'}
        return json.dumps(feedback()),{'done':True}
    monkeypatch.setattr(client,'generate_raw',raw)
    assert (await client.review_solution(p,'// student code','approach')).mode=='approach'
    assert len(calls)==2 and calls[1]['num_predict']<=1280

@pytest.mark.asyncio
async def test_review_failure_stops_after_two_calls(monkeypatch):
    client=OllamaClient();calls=[]
    async def raw(**kwargs):calls.append(kwargs);raise httpx.ReadTimeout('timeout')
    monkeypatch.setattr(client,'generate_raw',raw)
    with pytest.raises(ValueError):await client.review_solution(get_registry()[0],'// student code','approach')
    assert len(calls)==2

@pytest.mark.asyncio
async def test_lesson_wrong_identity_retries_and_context_is_selected_material(monkeypatch):
    client=OllamaClient();calls=[]; lesson=next(l for l in get_lessons() if l.id=='binary-search')
    async def raw(**kwargs):
        calls.append(kwargs)
        return json.dumps(lesson_feedback('other' if len(calls)==1 else lesson.id)),{'done':True}
    monkeypatch.setattr(client,'generate_raw',raw)
    result=await client.answer_lesson_question(lesson,'Why check bounds?')
    assert result.lesson_id==lesson.id and len(calls)==2
    assert lesson.intuition in calls[0]['prompt']
    assert 'Rotting Oranges' not in calls[0]['prompt']
    assert 'maxLength' not in calls[0]['response_schema']['properties']['answer']
    assert LessonAnswer.model_json_schema()['properties']['answer']['maxLength']==2000
    with pytest.raises(ValidationError):LessonAnswer.model_validate({**lesson_feedback(),'material_sections':['invented']})
    with pytest.raises(ValidationError):LessonAnswer.model_validate({**lesson_feedback(),'answer':'short'})
    with pytest.raises(ValidationError):LessonAnswer.model_validate({**lesson_feedback(),'answer':'x'*2001})

def test_adapter_failed_invalid_and_timeout_reviews_have_no_feedback():
    class Broken(LearningTutor):
        async def review_solution(self,*args):raise httpx.ReadTimeout('offline')
        async def answer_lesson_question(self,*args):return {**lesson_feedback(),'lesson_id':'other'}
    with TestClient(create_app(tutor_factory=Broken),base_url='http://127.0.0.1') as c:
        sid=start(c)
        result=c.post('/api/reviews',json=dict(problem_id='lc_167',code='draft',mode='approach',reveal_teaching_details=True),headers=headers(c))
        assert result.status_code==503 and 'feedback' not in result.json()
        assert c.get(f'/api/sessions/{sid}',headers=headers(c)).json()['unlocked_level']==0
        assert c.post('/api/lessons/binary-search/questions',json={'question':'Why check bounds?'},headers=headers(c)).status_code==503
