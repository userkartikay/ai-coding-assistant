import pytest
from backend.eval.evaluator import evaluate_problem, summarize, assessed_output, output_hash
from backend.eval.dataset import EVALUATION_DATASET
from backend.core.schemas import ProgressiveHintResponse, MistakeDiagnosisResponse
from backend.runner.schemas import ExecutionReport,TestVerdict


@pytest.mark.asyncio
async def test_evaluator_checks_all_five_levels_and_keeps_quality_separate():
    class Runner:
        calls=0
        def run_test_suite(self,*args,**kw):
            assert kw['trusted'] is True
            self.calls+=1
            return ExecutionReport(overall_verdict=TestVerdict.AC if self.calls==1 else TestVerdict.WA,
                compilation_success=True,total_tests=1,failing_evidence='Expected 1, got 0')
    class Tutor:
        levels=[]
        async def diagnose_mistake(self,**kw):
            return MistakeDiagnosisResponse(category='other',misconception_summary='A wrong transition.',
                guiding_question='What changes here?',suggested_focus_area='State update')
        async def get_progressive_hint(self,**kw):
            from test_tutor_remediation import payload
            self.levels.append(kw['level'].value)
            return ProgressiveHintResponse.model_validate(payload(kw['level'].value))
    tutor=Tutor();result=await evaluate_problem(Runner(),tutor,EVALUATION_DATASET[0])
    assert tutor.levels==[1,2,3,4,5]
    summary=summarize([result])
    assert summary['schema_valid_hints']==5
    assert summary['category_matches']==0
    assert summary['human_reviewed_outputs']==0
    assert summary['mean_factual_correctness'] is None
    assert summary['mean_teaching_usefulness'] is None
    assert result['hints']['5']['generated_code_verified'] is False


def test_human_ratings_apply_only_to_exact_output_hash():
    data={'guidance':'A specific response'}
    review={'reviewer':'Independent audit','reviewer_kind':'human','factual_correctness':1,'teaching_usefulness':2,
            'evidence':'Correct principle but inaccurate example index.'}
    reviews={output_hash(data):review}
    assert assessed_output(data,reviews)['quality_review']['factual_correctness']==1
    assert assessed_output({'guidance':'Changed output'},reviews)['quality_review'] is None


def test_human_ratings_must_include_evidence_and_valid_scores():
    data={'guidance':'response'}
    with pytest.raises(ValueError):
        assessed_output(data,{output_hash(data):{'reviewer':'audit','reviewer_kind':'human','factual_correctness':3,
            'teaching_usefulness':2,'evidence':'x'}})
