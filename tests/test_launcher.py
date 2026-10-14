import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
import pytest
from scripts import start_dev as launcher

@pytest.mark.parametrize('version',['v20.19.0','v22.12.0','v24.20.0'])
def test_supported_node(version): launcher.validate_node(version)

@pytest.mark.parametrize('version',['v18.0.0','v20.18.0','v21.0.0','v22.11.0','not a version'])
def test_incompatible_node_is_actionable(version):
    with pytest.raises(launcher.LaunchError): launcher.validate_node(version)

def test_pins_are_verified_without_importing_backend(monkeypatch):
    monkeypatch.setattr(launcher,'pinned_requirements',lambda:[('fastapi','1.0'),('uvicorn','2.0')])
    def version(name):
        if name=='uvicorn': raise launcher.importlib.metadata.PackageNotFoundError(name)
        return '0.9'
    monkeypatch.setattr(launcher.importlib.metadata,'version',version)
    assert launcher.missing_python_packages()==['fastapi: 0.9; need 1.0','uvicorn: missing; need 2.0']

def test_frontend_detects_missing_or_mismatched_install_and_optional_platform_packages(tmp_path,monkeypatch):
    monkeypatch.setattr(launcher,'FRONTEND',tmp_path)
    assert launcher.frontend_ready() is False
    modules=tmp_path/'node_modules';modules.mkdir()
    wanted={'packages':{'':{},'node_modules/react':{'version':'1'},'node_modules/platform':{'version':'2','optional':True}}}
    (tmp_path/'package-lock.json').write_text(json.dumps(wanted))
    (modules/'.package-lock.json').write_text(json.dumps({'packages':{'node_modules/react':{'version':'1'}}}))
    for name in ['vite/bin/vite.js','typescript/bin/tsc','react/package.json','react-dom/package.json','monaco-editor/package.json']:
        path=modules/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('installed')
    assert launcher.frontend_ready()
    (modules/'react'/'package.json').unlink()
    assert not launcher.frontend_ready()

@pytest.mark.parametrize('payload,available',[
    ({'models':[{'name':'qwen3.5:4b'}]},True),({'models':[{'name':'another-model'}]},False)])
def test_ollama_checks_exact_model_without_generating(monkeypatch,payload,available):
    monkeypatch.setattr(launcher,'fetch',lambda url:payload)
    assert launcher.ollama_status()[0] is available

def test_ollama_offline_does_not_block_offline_learning(monkeypatch):
    monkeypatch.setattr(launcher,'fetch',lambda url: (_ for _ in ()).throw(OSError('offline')))
    monkeypatch.setattr(launcher.shutil,'which',lambda name:None)
    ready,message=launcher.ollama_status();assert not ready and 'Install' in message

def prepare(monkeypatch):
    monkeypatch.setattr(launcher.shutil,'which',lambda name:'node' if name=='node' else 'npm')
    monkeypatch.setattr(launcher,'run',lambda *args,**kwargs:'v24.20.0')
    monkeypatch.setattr(launcher,'missing_python_packages',lambda:[])
    monkeypatch.setattr(launcher,'frontend_ready',lambda:True)
    monkeypatch.setattr(launcher,'ollama_status',lambda:(True,'ready'))
    monkeypatch.setattr(launcher,'port_busy',lambda port:False)

def test_check_never_starts_or_installs(monkeypatch):
    prepare(monkeypatch)
    monkeypatch.setattr(launcher,'supervise',lambda *args:pytest.fail('check must not start'))
    monkeypatch.setattr(launcher,'setup',lambda *args:pytest.fail('check must not install'))
    assert launcher.main(['--check'])==0

def test_missing_dependencies_require_explicit_setup(monkeypatch,capsys):
    prepare(monkeypatch);monkeypatch.setattr(launcher,'missing_python_packages',lambda:['fastapi missing'])
    monkeypatch.setattr(launcher,'setup',lambda *args:pytest.fail('no automatic install'))
    assert launcher.main([])==1
    assert '--setup' in capsys.readouterr().err

def test_unrelated_port_owner_is_not_killed(monkeypatch):
    monkeypatch.setattr(launcher,'port_busy',lambda port:True)
    monkeypatch.setattr(launcher,'backend_ready',lambda:False)
    monkeypatch.setattr(launcher,'stop_owned',lambda process:pytest.fail('must not stop unrelated services'))
    with pytest.raises(launcher.LaunchError,match='unrecognized'):launcher.supervise('node')

def test_reuses_services_without_starting_or_stopping(monkeypatch):
    monkeypatch.setattr(launcher,'port_busy',lambda port:True)
    monkeypatch.setattr(launcher,'backend_ready',lambda:True)
    monkeypatch.setattr(launcher,'frontend_server_ready',lambda:True)
    monkeypatch.setattr(launcher,'proxy_ready',lambda:True)
    monkeypatch.setattr(launcher,'fetch',lambda *args,**kwargs:{'api':'ready','execution_enabled':False})
    monkeypatch.setattr(launcher.subprocess,'Popen',lambda *args,**kwargs:pytest.fail('must reuse'))
    launcher.supervise('node')

def test_failed_second_start_cleans_first_owned_process(tmp_path,monkeypatch):
    monkeypatch.setattr(launcher,'ROOT',tmp_path)
    monkeypatch.setattr(launcher,'port_busy',lambda port:False)
    owned=type('Owned',(),{})();stopped=[];calls=[]
    def popen(*args,**kwargs):
        calls.append(args)
        if len(calls)==2: raise OSError('frontend spawn failed')
        return owned
    monkeypatch.setattr(launcher.subprocess,'Popen',popen)
    monkeypatch.setattr(launcher,'wait_ready',lambda *args:None)
    monkeypatch.setattr(launcher,'stop_owned',stopped.append)
    with pytest.raises(OSError):launcher.supervise('node')
    assert stopped==[owned]

def test_setup_skips_matching_dependencies(monkeypatch,tmp_path,capsys):
    monkeypatch.setattr(launcher,'ROOT',tmp_path)
    target=tmp_path/'.venv'/('Scripts/python.exe' if launcher.os.name=='nt' else 'bin/python')
    target.parent.mkdir(parents=True);target.write_text('existing')
    calls=[]
    monkeypatch.setattr(launcher,'run',lambda command,**kwargs:(calls.append(command) or '[]'))
    monkeypatch.setattr(launcher,'frontend_ready',lambda:True)
    launcher.setup('node')
    assert len(calls)==1 and '-c' in calls[0]
    assert 'skipping pip' in capsys.readouterr().out

def test_explicit_setup_creates_environment_and_installs_only_missing_dependencies(monkeypatch,tmp_path):
    monkeypatch.setattr(launcher,'ROOT',tmp_path)
    calls=[]
    def command(command,**kwargs):
        calls.append(command)
        return '["fastapi missing"]' if '-c' in command else ''
    monkeypatch.setattr(launcher,'run',command)
    monkeypatch.setattr(launcher,'frontend_ready',lambda:True)
    launcher.setup('node')
    assert calls[0][1:3]==['-m','venv']
    assert calls[-1][1:5]==['-m','pip','install','-r']
    assert len(calls)==3  # No npm ci when the frontend already matches.

def test_cleanup_waits_for_real_owned_process_tree():
    # Repository-authored helper, not student code. Verifies launch cleanup only.
    source="import subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);print(p.pid,flush=True);time.sleep(60)"
    process=subprocess.Popen([sys.executable,'-c',source],stdout=subprocess.PIPE,text=True)
    child=int(process.stdout.readline())
    try:
        launcher.stop_owned(process)
        assert process.poll() is not None
        assert not psutil.pid_exists(child)
    finally:
        if process.poll() is None:process.kill();process.wait()
        process.stdout.close()
