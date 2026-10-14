"""Sequential production-tier latency measurements, with structural success recorded.

Writes a new JSON evidence file, preserving historical benchmark documents.
Schema compliance is not a measurement of educational correctness.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.core.ollama_client import OllamaClient
from backend.core.schemas import HintLevel
from backend.eval.dataset import EVALUATION_DATASET


class MeasuredClient(OllamaClient):
    def __init__(self):super().__init__();self.calls=[]
    async def generate_raw(self,**kwargs):
        raw,data=await super().generate_raw(**kwargs)
        self.calls.append({k:data.get(k) for k in ('done','done_reason','eval_count','eval_duration','prompt_eval_count','load_duration')})
        return raw,data


async def main():
    p=EVALUATION_DATASET[0];client=MeasuredClient();rows=[]
    for level in HintLevel:
        client.calls=[];started=time.perf_counter();error=None
        try:
            await client.get_progressive_hint(level,p.title,p.description,p.constraints,p.primary_pattern,p.subpattern,function_signature=p.function_signature)
        except Exception as exc:error=type(exc).__name__
        row={'level':level.value,'wall_seconds':round(time.perf_counter()-started,2),
             'schema_compliant':error is None,'error':error,'calls':client.calls}
        rows.append(row);print(json.dumps(row),flush=True)
    Path('docs/LATENCY_MEASUREMENTS.json').write_text(json.dumps({'model':client.model,'tiers':rows,
        'limitations':'Sequential wall latency includes any recovery. Structural success is not teaching-quality proof; no fixed speed/offload claims.'},indent=2),encoding='utf-8')


if __name__=='__main__':asyncio.run(main())
