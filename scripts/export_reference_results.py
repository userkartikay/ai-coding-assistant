"""Explicit local export of repository-authored trusted fixtures. No browser input.

Run manually: python scripts/export_reference_results.py
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.eval.dataset import EVALUATION_DATASET
from backend.runner.cpp_runner import CppRunner
from backend.runner.schemas import TestVerdict
from backend.api.references import fingerprint, display_report


def main():
    runner = CppRunner()
    artifact = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'problems': {}}
    for p in EVALUATION_DATASET:
        reports = {}
        for label, code in [('canonical', p.canonical_solution), ('known_bug', p.buggy_submission)]:
            report = runner.run_test_suite(p.harness_template.replace('// STUDENT_CODE_PLACEHOLDER', code), p.test_cases, trusted=True)
            if label == 'canonical' and report.overall_verdict != TestVerdict.AC:
                raise RuntimeError(f'Canonical verification failed for {p.id}')
            if label == 'known_bug' and report.overall_verdict == TestVerdict.AC:
                raise RuntimeError(f'Known bug unexpectedly accepted for {p.id}')
            reports[label] = display_report(report)
        artifact['problems'][p.id] = {'fingerprint': fingerprint(p), 'reports': reports}
        print(f'{p.id}: trusted canonical AC / known bug {reports["known_bug"]["overall_verdict"]}', flush=True)
    output = Path(__file__).resolve().parents[1]/'docs'/'REFERENCE_RESULTS.json'
    output.write_text(json.dumps(artifact, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
