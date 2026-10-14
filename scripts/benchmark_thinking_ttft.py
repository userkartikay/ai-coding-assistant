"""Measure raw response chunks and validated hint completion separately.

Thinking chunks are not user guidance; NDJSON chunk counts are not token counts.
This measures a structured L1 request, not future SSE UI performance.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from backend.core.prompts import build_hint_prompt,SYSTEM_PROMPT_SOCRATIC_TUTOR
from backend.core.schemas import HintLevel,ProgressiveHintResponse
from backend.eval.dataset import EVALUATION_DATASET


class StreamingMeasurement:
    def __init__(self):
        self.first_response_ms=None
        self.text=''
        self.telemetry={}
    def record(self,data,elapsed_ms):
        piece=data.get('response','')
        if piece:
            if self.first_response_ms is None:self.first_response_ms=elapsed_ms
            self.text+=piece
        if data.get('done'):self.telemetry=data
    def result(self,elapsed_ms):
        valid=False
        if self.telemetry.get('done_reason')!='length':
            try:
                hint=ProgressiveHintResponse.model_validate_json(self.text)
                valid=hint.level==HintLevel.LEVEL_1_NUDGE
            except ValueError:pass
        return {'first_response_chunk_ms':self.first_response_ms,
                'validated_hint_ms':elapsed_ms if valid else None,
                'schema_compliant':valid,'completion_tokens':self.telemetry.get('eval_count'),
                'eval_duration_ns':self.telemetry.get('eval_duration'),
                'limitations':'First JSON bytes are not necessarily usable guidance; thinking ignored. No UI latency guarantee.'}


async def main():
    p=EVALUATION_DATASET[0];measurement=StreamingMeasurement();started=time.perf_counter()
    payload={'model':'qwen3.5:4b','prompt':build_hint_prompt(HintLevel(1),p.title,p.description,p.constraints),
             'system':SYSTEM_PROMPT_SOCRATIC_TUTOR,'stream':True,'think':False,
             'format':ProgressiveHintResponse.model_json_schema(),
             'options':{'num_ctx':4096,'num_predict':256,'temperature':.1}}
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream('POST','http://localhost:11434/api/generate',json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():measurement.record(json.loads(line),(time.perf_counter()-started)*1000)
    result=measurement.result((time.perf_counter()-started)*1000)
    Path('docs/STREAMING_MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':asyncio.run(main())
