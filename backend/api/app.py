"""Thin localhost adapter. Browser submissions are NEVER compiled or executed.

Hint rules come from SocraticCliApp, metadata from the existing registry. Sessions
are bounded in-memory state, not a replacement for SQLite. Ollama stays server-side.
"""
import asyncio
import json
from pathlib import Path
import secrets
import time
import httpx
from dataclasses import dataclass, field
from typing import Literal
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field
from backend.cli.interactive_cli import SocraticCliApp
from backend.core.ollama_client import OllamaClient
from backend.curriculum.registry import get_registry
from backend.curriculum.content import SUMMARIES
from backend.curriculum.lessons import get_lessons
from backend.core.learning import ReviewRequest, SolutionReview, LessonQuestion, LessonAnswer
from backend.eval.dataset import EVALUATION_DATASET
from backend.runner.schemas import ExecutionReport, TestCaseResult, TestVerdict
from backend.api.references import fingerprint

ROOT = Path(__file__).resolve().parents[2]
ORIGINS = ['http://127.0.0.1:5173', 'http://localhost:5173',
           'http://127.0.0.1:8000', 'http://localhost:8000']


class SessionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    problem_id: str = Field(max_length=30)


class HintRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    level: int = Field(ge=1, le=5, strict=True)


@dataclass
class Session:
    app: SocraticCliApp
    touched: float = field(default_factory=time.monotonic)
    hints: dict = field(default_factory=dict)


def create_app(tutor_factory=OllamaClient, reference_path=ROOT/'docs'/'REFERENCE_RESULTS.json'):
    api = FastAPI(title='AI Coding Mentor — local adapter', docs_url='/api/docs', openapi_url='/api/openapi.json')
    api.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost'])
    api.add_middleware(CORSMiddleware, allow_origins=ORIGINS,
                       allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-Mentor-Token'])
    token = secrets.token_urlsafe(32)
    sessions = {}
    model_lock = asyncio.Lock()
    registry = {p.id: p for p in get_registry()}
    lessons = {l.id: l for l in get_lessons()}
    fixture_indices = {p.id: i for i, p in enumerate(EVALUATION_DATASET)}
    api.state.sessions = sessions

    def authorized(request: Request):
        origin = request.headers.get('origin')
        if origin and origin not in ORIGINS:
            raise HTTPException(403, 'Only the local frontend may make this request.')
        if not secrets.compare_digest(request.headers.get('x-mentor-token', ''), token):
            raise HTTPException(403, 'Local session token missing or stale. Reload the page.')

    def problem(problem_id):
        if problem_id not in registry:
            raise HTTPException(404, 'Problem not found.')
        return registry[problem_id]

    def session(session_id):
        entry = sessions.get(session_id)
        if entry is None or time.monotonic() - entry.touched > 7200:
            sessions.pop(session_id, None)
            raise HTTPException(410, 'Mentor session expired. Start a new session; your local draft is unaffected.')
        entry.touched = time.monotonic()
        return entry

    def session_payload(session_id, entry):
        return {'id': session_id, 'problem_id': entry.app.active_problem.id,
                'unlocked_level': entry.app.unlocked_hint_level, 'hints': entry.hints}

    @api.get('/api/bootstrap')
    def bootstrap():
        return {'token': token, 'model': 'qwen3.5:4b', 'execution_enabled': False,
                'hint_streaming': False, 'session_lifetime_seconds': 7200}

    @api.get('/api/health')
    async def health():
        return {'api': 'ready', 'model': 'qwen3.5:4b',
                'tutor_available': await tutor_factory().check_health(),
                'execution_enabled': False, 'hint_streaming': False}

    @api.get('/api/problems')
    def catalogue():
        return [{'id': p.id, 'leetcode_id': p.metadata.leetcode_id, 'title': p.metadata.title,
                 'difficulty': p.metadata.difficulty.value, 'pattern': p.metadata.primary_pattern,
                 'subpattern': p.metadata.subpattern, 'executable': p.is_executable,
                 'provenance': p.metadata.provenance.value} for p in registry.values()]

    @api.get('/api/lessons')
    def lesson_list():
        return [l.model_dump(mode='json') for l in lessons.values()]

    async def generate_learning(operation):
        if model_lock.locked():
            raise HTTPException(409, 'The local mentor is working on another request. Retry after it finishes.')
        async with model_lock:
            try:
                return await operation()
            except (ValueError, httpx.HTTPError) as exc:
                raise HTTPException(503, 'The mentor could not produce valid feedback. No hints were unlocked. Retry or shorten your input.') from exc

    @api.post('/api/reviews', dependencies=[Depends(authorized)])
    async def review(body: ReviewRequest):
        p = problem(body.problem_id)
        # Only known statements currently provide sufficiently verified review grounding.
        if not p.is_executable:
            raise HTTPException(409, 'Review is unavailable until this question has verified statement grounding.')
        async def operation():
            response = SolutionReview.model_validate(await tutor_factory().review_solution(p,body.code,body.mode))
            if response.mode != body.mode:
                raise ValueError('Generated review mode mismatch')
            return {'source':'ai_review','student_code_executed':False,
                    'problem_id':p.id,'feedback':response.model_dump(mode='json')}
        return await generate_learning(operation)

    @api.post('/api/lessons/{lesson_id}/questions', dependencies=[Depends(authorized)])
    async def lesson_question(lesson_id: str, body: LessonQuestion):
        if lesson_id not in lessons:
            raise HTTPException(404, 'Lesson not found.')
        async def operation():
            response = LessonAnswer.model_validate(await tutor_factory().answer_lesson_question(lessons[lesson_id],body.question))
            if response.lesson_id != lesson_id:
                raise ValueError('Generated lesson identity mismatch')
            return {'source':'ai_lesson','feedback':response.model_dump(mode='json')}
        return await generate_learning(operation)

    @api.get('/api/problems/{problem_id}')
    def detail(problem_id: str):
        p = problem(problem_id)
        fixture = p.execution
        return {'id': p.id, 'metadata': p.metadata.model_dump(mode='json'),
                'executable': p.is_executable,
                'description': fixture.description if fixture else SUMMARIES.get(p.metadata.leetcode_id),
                'constraints': fixture.constraints if fixture else None,
                'function_signature': fixture.function_signature if fixture else None,
                'starter_code': (fixture.function_signature + ' {\n    // Write your approach here.\n}\n') if fixture else '',
                'examples': [t.model_dump() for t in fixture.test_cases[:2] if not t.is_hidden] if fixture else [],
                'test_count': len(fixture.test_cases) if fixture else 0}

    @api.post('/api/sessions', dependencies=[Depends(authorized)])
    def new_session(body: SessionRequest):
        p = problem(body.problem_id)
        if not p.is_executable:
            raise HTTPException(409, 'This catalogue-only question has no verified statement for tutor grounding yet.')
        now = time.monotonic()
        for key in list(sessions):
            if now - sessions[key].touched > 7200:
                del sessions[key]
        if len(sessions) >= 100:
            raise HTTPException(429, 'Local mentor session limit reached; restart the API or wait for expiry.')
        app = SocraticCliApp(tutor=tutor_factory())  # execution disabled, no database writes
        app.select_problem(fixture_indices[p.id])
        sid = secrets.token_urlsafe(24)
        sessions[sid] = Session(app)
        return session_payload(sid, sessions[sid])

    @api.get('/api/sessions/{session_id}', dependencies=[Depends(authorized)])
    def get_session(session_id: str):
        return session_payload(session_id, session(session_id))

    @api.post('/api/sessions/{session_id}/hints', dependencies=[Depends(authorized)])
    async def hint(session_id: str, body: HintRequest):
        entry = session(session_id)
        if body.level in entry.hints:
            return session_payload(session_id, entry)
        if model_lock.locked():
            raise HTTPException(409, 'The local mentor is working on another request. Retry after it finishes.')
        async with model_lock:
            try:
                response = await entry.app.request_progressive_hint(body.level)
            except ValueError as exc:
                status = 409 if body.level > entry.app.unlocked_hint_level + 1 else 503
                raise HTTPException(status, str(exc)) from exc
            if entry.app.unlocked_hint_level < body.level:
                # The CLI's neutral fallback is not a successfully generated/unlocked tier.
                raise HTTPException(503, 'The mentor could not generate a valid hint. No level was unlocked. Retry when Ollama is available.')
            entry.hints[body.level] = response.model_dump(mode='json')
            entry.touched = time.monotonic()
            return session_payload(session_id, entry)

    @api.get('/api/problems/{problem_id}/reference-results')
    def reference_results(problem_id: str):
        p = problem(problem_id)
        if not p.is_executable:
            raise HTTPException(404, 'No executable reference suite is available.')
        try:
            artifact = json.loads(Path(reference_path).read_text(encoding='utf-8'))
            entry = artifact['problems'][problem_id]
            if entry['fingerprint'] != fingerprint(p.execution):
                raise ValueError('stale')
            for label in ('canonical', 'known_bug'):
                report = ExecutionReport.model_validate(entry['reports'][label])
                if report.total_tests != len(p.execution.test_cases):
                    raise ValueError('inconsistent suite')
        except (OSError, KeyError, ValueError, TypeError):
            raise HTTPException(404, 'Reference reports are unavailable or stale. Export trusted fixtures locally first.')
        return {'source': 'trusted_reference', 'student_code_executed': False,
                'recorded_at': artifact['recorded_at'], **entry}

    @api.get('/api/problems/{problem_id}/mock-results')
    def mock_results(problem_id: str, scenario: Literal['AC', 'WA', 'COMPILATION_ERROR', 'TLE', 'RUNTIME_ERROR'] = 'WA'):
        p = problem(problem_id)
        if not p.is_executable:
            raise HTTPException(404, 'No verified cases available for this display preview.')
        tc = p.execution.test_cases[0]
        verdict = TestVerdict(scenario)
        result = TestCaseResult(test_case_id=tc.id, passed=verdict==TestVerdict.AC, verdict=verdict,
            input_data=tc.input_data, expected_output=tc.expected_output,
            actual_output=tc.expected_output if verdict==TestVerdict.AC else 'Illustrative mock output',
            error_message='Illustrative process failure; your code was not executed.' if verdict in (TestVerdict.TLE,TestVerdict.RUNTIME_ERROR) else None)
        report = ExecutionReport(overall_verdict=verdict, compilation_success=verdict!=TestVerdict.COMPILATION_ERROR,
            compilation_output='Illustrative compiler diagnostic: error: expected expression.' if verdict==TestVerdict.COMPILATION_ERROR else '',
            total_tests=1, passed_tests=int(verdict==TestVerdict.AC), test_results=[] if verdict==TestVerdict.COMPILATION_ERROR else [result])
        return {'source': 'mock', 'student_code_executed': False, 'report': report.model_dump(mode='json')}

    @api.api_route('/api/{unknown:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def unavailable(unknown: str):
        raise HTTPException(404, 'Endpoint unavailable. Browser code execution is not supported.')

    # The same safe API can serve the built frontend without another web server.
    if (ROOT/'frontend'/'dist'/'index.html').exists():
        api.mount('/', StaticFiles(directory=ROOT/'frontend'/'dist', html=True), name='frontend')
    return api


app = create_app()
