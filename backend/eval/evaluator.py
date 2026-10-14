"""Sequential teaching evaluation. Structural checks and human quality scores are separate.

Default: all ten fixed mistakes and all five tiers. No generated solution is executed:
model output is untrusted. Human ratings must identify the exact output hash.
"""
import argparse
import asyncio
import hashlib
import json
import time
from pathlib import Path
import sys
from typing import Literal
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pydantic import BaseModel, Field
from backend.runner.cpp_runner import CppRunner
from backend.runner.schemas import TestVerdict
from backend.core.ollama_client import OllamaClient
from backend.core.schemas import HintLevel, has_code
from backend.eval.dataset import EVALUATION_DATASET


class QualityReview(BaseModel):
    reviewer: str = Field(min_length=1)
    reviewer_kind: Literal['human', 'ai']
    factual_correctness: int = Field(ge=0, le=2)
    teaching_usefulness: int = Field(ge=0, le=2)
    evidence: str = Field(min_length=10)


def output_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _check_leakage(text):
    return has_code(text)


def assessed_output(data, reviews):
    digest = output_hash(data)
    review = QualityReview.model_validate(reviews[digest]).model_dump() if digest in reviews else None
    return {'response': data, 'output_sha256': digest, 'schema_compliant': True,
            'quality_review': review, 'quality_status': 'reviewed' if review else 'unreviewed'}


async def evaluate_problem(runner, client, problem, *, levels=(1,2,3,4,5), reviews=None):
    reviews = reviews or {}
    source = lambda code: problem.harness_template.replace('// STUDENT_CODE_PLACEHOLDER', code)
    canonical = runner.run_test_suite(source(problem.canonical_solution), problem.test_cases, trusted=True)
    buggy = runner.run_test_suite(source(problem.buggy_submission), problem.test_cases, trusted=True)
    result = {'problem_id': problem.id, 'title': problem.title,
              'canonical_verdict': canonical.overall_verdict.value,
              'buggy_verdict': buggy.overall_verdict.value, 'hints': {}}
    if canonical.overall_verdict != TestVerdict.AC or buggy.overall_verdict == TestVerdict.AC:
        result['execution_error'] = 'Fixture verification failed; tutor evaluation withheld'
        return result
    try:
        diagnosis = await client.diagnose_mistake(problem_title=problem.title,
            problem_description=problem.description, target_complexity=problem.target_complexity,
            student_code=problem.buggy_submission, test_failure_evidence=buggy.failing_evidence)
        data = diagnosis.model_dump(mode='json')
        result['diagnosis'] = assessed_output(data, reviews)
        result['diagnosis']['category_matches_expected'] = diagnosis.category == problem.intended_mistake_category
        result['diagnosis']['expected_category'] = problem.intended_mistake_category.value
        result['diagnosis']['obvious_code_leakage'] = has_code(' '.join(map(str,data.values())))
    except Exception as exc:
        result['diagnosis'] = {'schema_compliant': False, 'error': type(exc).__name__, 'quality_status':'unreviewed'}
    for level in levels:
        started = time.perf_counter()
        try:
            hint = await client.get_progressive_hint(level=HintLevel(level),problem_title=problem.title,
                problem_description=problem.description, constraints=problem.constraints,
                primary_pattern=problem.primary_pattern,subpattern=problem.subpattern,
                function_signature=problem.function_signature)
            data = hint.model_dump(mode='json')
            item = assessed_output(data,reviews)
            item['requested_level_matches'] = hint.level.value == level
            item['obvious_code_leakage'] = has_code(' '.join(str(v) for v in data.values() if v)) if level<=3 else False
            item['generated_code_verified'] = False if level==5 else None
            result['hints'][str(level)] = item
        except Exception as exc:
            result['hints'][str(level)] = {'schema_compliant':False,'error':type(exc).__name__,'quality_status':'unreviewed'}
        result['hints'][str(level)]['latency_seconds'] = round(time.perf_counter() - started, 2)
        print(f"{problem.id}: tier {level} recorded",flush=True)
    return result


def summarize(results):
    hints = [h for p in results for h in p.get('hints',{}).values()]
    diagnoses = [p['diagnosis'] for p in results if 'diagnosis' in p]
    outputs = hints + diagnoses
    reviewed = [o['quality_review'] for o in outputs if o.get('quality_review')]
    return {'problems':len(results), 'hint_outputs':len(hints),
        'schema_valid_hints':sum(h.get('schema_compliant',False) for h in hints),
        'category_matches':sum(d.get('category_matches_expected',False) for d in diagnoses),
        'diagnoses_attempted':len(diagnoses),
        'heuristic_leak_flags':sum(o.get('obvious_code_leakage',False) for o in outputs),
        'reviewed_outputs':len(reviewed),
        'human_reviewed_outputs':sum(r['reviewer_kind']=='human' for r in reviewed),
        'ai_reviewed_outputs':sum(r['reviewer_kind']=='ai' for r in reviewed),
        'mean_factual_correctness':sum(r['factual_correctness'] for r in reviewed)/len(reviewed) if reviewed else None,
        'mean_teaching_usefulness':sum(r['teaching_usefulness'] for r in reviewed)/len(reviewed) if reviewed else None,
        'limitations':'Schema compliance, category matching, and regex checks do not establish educational correctness. Unreviewed outputs have no quality score. Generated code has not been judged.'}


async def run_full_evaluation(problem_ids=None,levels=(1,2,3,4,5),reviews=None):
    runner=CppRunner();client=OllamaClient();results=[]
    for p in EVALUATION_DATASET:
        if problem_ids and p.id not in problem_ids:continue
        results.append(await evaluate_problem(runner,client,p,levels=levels,reviews=reviews))
    return {'model':client.model,'results':results,'summary':summarize(results)}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--problem',action='append',choices=[p.id for p in EVALUATION_DATASET])
    parser.add_argument('--reviews',type=Path,help='JSON mapping exact output SHA256 to reviewer, reviewer_kind (human/ai), 0-2 factual and usefulness scores, and evidence')
    parser.add_argument('--output',type=Path,default=Path('docs/REMEDIATION_EVALUATION.json'))
    args=parser.parse_args()
    reviews=json.loads(args.reviews.read_text(encoding='utf-8')) if args.reviews else {}
    report=asyncio.run(run_full_evaluation(args.problem,reviews=reviews))
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report['summary'],indent=2))
