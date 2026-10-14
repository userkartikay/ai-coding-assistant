"""Small live Qwen sample. Structural results are separate from subjective review.

No source execution. Sequential calls fit the single-model local hardware budget.
Run manually: python -m scripts.evaluate_learning
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from backend.core.ollama_client import OllamaClient
from backend.curriculum.registry import get_registry
from backend.curriculum.lessons import get_lessons

async def main(only_bug=False):
    client=OllamaClient(); registry={p.id:p for p in get_registry()}
    lessons={l.id:l for l in get_lessons()}
    jobs=[
        ('buggy_pair_review','review','lc_167','approach',
         'vector<int> twoSum(vector<int>& numbers, int target) { int l=0, r=(int)numbers.size()-1; while(l<r) { int sum=numbers[l]+numbers[r]; if(sum==target) return {l+1,r+1}; ++l; --r; } return {}; }'),
        ('correct_search_review','review','lc_704','approach',
         'int search(vector<int>& nums,int target) { int l=0,r=(int)nums.size()-1; while(l<=r) { int m=l+(r-l)/2; if(nums[m]==target) return m; if(nums[m]<target) l=m+1; else r=m-1; } return -1; }'),
        ('pair_alternative_comparison','review','lc_167','compare',
         'vector<int> twoSum(vector<int>& numbers,int target) { for(int i=0;i<(int)numbers.size();++i) for(int j=i+1;j<(int)numbers.size();++j) if(numbers[i]+numbers[j]==target) return {i+1,j+1}; return {}; }'),
        ('binary_boundary_followup','lesson','binary-search',None,'Why can lower bound equal the array size, and when is reading that index unsafe?'),
        ('window_followup','lesson','sliding-window',None,'Why must I update character counts when the left boundary moves?'),
    ]
    if only_bug: jobs=jobs[:1]
    report=dict(model=client.model,recorded_at=datetime.now(timezone.utc).isoformat(),
        scope='Five sequential static-review/lesson samples; not a teaching reliability benchmark.',
        automated_schema_results=[],subjective_quality_review=[])
    output=Path('docs/LEARNING_REVIEW_TRACE_CHECK.json' if only_bug else 'docs/LEARNING_EVALUATION.json')
    original_generate=client.generate_raw
    attempts=[]
    async def record_generation(**kwargs):
        raw,metadata=await original_generate(**kwargs)
        attempts.append(dict(response=raw,done=metadata.get('done'),done_reason=metadata.get('done_reason'),
                             prompt_tokens=metadata.get('prompt_eval_count'),completion_tokens=metadata.get('eval_count')))
        return raw,metadata
    client.generate_raw=record_generation
    for name,kind,identity,mode,text in jobs:
        attempts.clear()
        start=time.perf_counter()
        row=dict(case=name,kind=kind,identity=identity,mode=mode)
        try:
            result=await (client.review_solution(registry[identity],text,mode) if kind=='review'
                          else client.answer_lesson_question(lessons[identity],text))
            row.update(structural_success=True,response=result.model_dump(mode='json'))
        except Exception as exc:
            row.update(structural_success=False,error=f'{type(exc).__name__}: {exc}')
        row['seconds']=round(time.perf_counter()-start,2)
        row['generation_attempts']=list(attempts)
        report['automated_schema_results'].append(row)
        output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(f"{name}: structural={row['structural_success']} {row['seconds']}s",flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--bug-probe',action='store_true',help='Recheck the known simultaneous-pointer bug with the final source-tracing prompt')
    asyncio.run(main(parser.parse_args().bug_probe))
