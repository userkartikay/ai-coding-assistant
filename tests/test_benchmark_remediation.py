from scripts.benchmark_thinking_ttft import StreamingMeasurement
from backend.core.schemas import ProgressiveHintResponse


def test_thinking_chunks_are_not_hint_latency_or_tokens():
    measurement=StreamingMeasurement()
    measurement.record({'thinking':'private thought'},10)
    measurement.record({'thinking':'more private thought'},20)
    assert measurement.first_response_ms is None
    measurement.record({'response':'{"level":1,'},30)
    measurement.record({'response':'"title":"Nudge","guidance":"Observe the constraints.","guiding_question":"Which property matters?","contains_code":false}'},40)
    measurement.record({'done':True,'done_reason':'stop','eval_count':80,'eval_duration':1000000},50)
    result=measurement.result(50)
    assert result['first_response_chunk_ms']==30
    assert result['validated_hint_ms']==50
    assert result['completion_tokens']==80
    assert 'private' not in measurement.text


def test_truncated_stream_is_not_a_valid_hint():
    measurement=StreamingMeasurement()
    measurement.record({'response':'{"level":1'},20)
    measurement.record({'done':True,'done_reason':'length','eval_count':256},50)
    result=measurement.result(50)
    assert result['validated_hint_ms'] is None and not result['schema_compliant']
