import os
import sys
import psutil
import pytest
from backend.runner.process import run_bounded
from backend.runner.cpp_runner import CppRunner
from backend.runner.schemas import TestVerdict, TestCase
from backend.cli.interactive_cli import SocraticCliApp
from backend.eval.dataset import EVALUATION_DATASET


def test_empty_suite_rejected_before_compilation():
    with pytest.raises(ValueError,match='non-empty'):
        CppRunner().run_test_suite('int main(){}',[],trusted=True)


def test_trusted_acknowledgement_required(tmp_path):
    runner=CppRunner();case=TestCase(id='t',input_data='',expected_output='')
    with pytest.raises(PermissionError):runner.run_test_suite('int main(){}',[case])
    with pytest.raises(PermissionError):runner.compile('int main(){}',str(tmp_path))
    with pytest.raises(PermissionError):runner.execute_test('unknown',[case][0])
    app=SocraticCliApp();app.select_problem(0)
    with pytest.raises(PermissionError):app.submit_code(app.active_problem.canonical_solution)


@pytest.mark.parametrize('pipe', ['stdout','stderr'])
def test_infinite_output_is_bounded_during_execution(tmp_path,pipe):
    code=f'import os\nwhile True: os.write({1 if pipe=="stdout" else 2}, b"x"*4096)'
    result=run_bounded([sys.executable,'-c',code],cwd=str(tmp_path),timeout=3,output_limit=128)
    assert result.reason=='output'
    assert result.stdout_bytes<=128 and result.stderr_bytes<=128
    assert result.elapsed_ms<2500


def test_compiler_diagnostics_are_bounded(tmp_path):
    code='\n'.join('#warning flooding compiler diagnostics' for _ in range(2000))+'\nint main(){}'
    success,output,_,_=CppRunner(max_output_bytes=256).compile(code,str(tmp_path),trusted=True)
    assert not success
    assert 'output' in output.lower()
    assert len(output.encode('utf-8'))<1024


def test_timeout_terminates_observed_child(tmp_path):
    code='import subprocess,sys,time\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"])\nprint(p.pid,flush=True)\ntime.sleep(30)'
    result=run_bounded([sys.executable,'-c',code],cwd=str(tmp_path),timeout=.7)
    assert result.reason=='timeout'
    child=int(result.stdout.strip())
    assert not psutil.pid_exists(child)


def test_sampled_memory_limit_stops_large_allocation(tmp_path):
    result=run_bounded([sys.executable,'-c','import time; x=bytearray(64*1024*1024);time.sleep(5)'],
        cwd=str(tmp_path),timeout=3,memory_limit_mb=32)
    assert result.reason=='memory'


def test_stairs_one_bug_no_longer_accepted():
    p=next(p for p in EVALUATION_DATASET if p.leetcode_id==70)
    bad=p.canonical_solution.replace('if (n <= 2) return n;', 'if (n == 1) return 0; if (n == 2) return n;')
    report=CppRunner().run_test_suite(p.harness_template.replace('// STUDENT_CODE_PLACEHOLDER',bad),p.test_cases,trusted=True)
    assert report.overall_verdict==TestVerdict.WA
    assert any(r.test_case_id=='stairs_one' and not r.passed for r in report.test_results)


def test_islands_maximum_input_accepted():
    p=next(p for p in EVALUATION_DATASET if p.leetcode_id==200)
    case=next(t for t in p.test_cases if t.id=='island_max')
    report=CppRunner().run_test_suite(p.harness_template.replace('// STUDENT_CODE_PLACEHOLDER',p.canonical_solution),[case],trusted=True)
    assert report.overall_verdict==TestVerdict.AC


def test_ac_display_is_limited_to_verified_suite():
    from backend.runner.schemas import ExecutionReport
    text=SocraticCliApp().format_verdict_display(ExecutionReport(overall_verdict=TestVerdict.AC,compilation_success=True,total_tests=1,passed_tests=1))
    assert 'available verified suite' in text
    assert 'not a proof for all inputs' in text
