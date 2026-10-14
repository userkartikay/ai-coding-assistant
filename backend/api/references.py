"""Read-only, fingerprinted reports exported by an explicit trusted-local script."""
import hashlib
import json
from backend.eval.dataset import EvalProblem


def fingerprint(problem: EvalProblem) -> str:
    return hashlib.sha256(problem.model_dump_json().encode()).hexdigest()


def display_report(report):
    """Bound large fixture inputs for display, without changing recorded verdicts."""
    data = report.model_dump(mode='json')
    for key in ('compilation_output', 'failing_evidence'):
        if data.get(key) and len(data[key]) > 3000:
            data[key] = data[key][:3000] + '\n[Display excerpt]'
    for result in data['test_results']:
        result['truncated_fields'] = []
        for key in ('input_data', 'actual_output', 'expected_output', 'error_message'):
            if result.get(key) and len(result[key]) > 1200:
                result[key] = result[key][:1200] + '\n[Display excerpt]'
                result['truncated_fields'].append(key)
    return data
