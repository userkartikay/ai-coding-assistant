"""Local development supervisor. No execution endpoint, migrations, or admin rights.

Default launch never installs dependencies. --setup is an explicit one-time repair;
--check is read-only. Only processes started by this invocation are stopped.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import build_opener, ProxyHandler

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / 'frontend'
MODEL = 'qwen3.5:4b'
# Loopback requests must not inherit an HTTP proxy configured for Internet traffic.
HTTP = build_opener(ProxyHandler({}))

class LaunchError(Exception):
    pass

def run(command, *, cwd=ROOT, timeout=30):
    try:
        return subprocess.run(command,cwd=cwd,check=True,capture_output=True,text=True,
                              timeout=timeout,encoding='utf-8',errors='replace').stdout.strip()
    except (OSError,subprocess.SubprocessError) as exc:
        detail=(getattr(exc,'stderr','') or str(exc))[-1800:]
        raise LaunchError(f"Command failed: {command[0]}\n{detail}") from exc

def pinned_requirements():
    pins=[]
    for line in (ROOT/'requirements-web.txt').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            name,version=line.strip().split('==');pins.append((name,version))
    return pins

def missing_python_packages():
    missing=[]
    for name,expected in pinned_requirements():
        try: actual=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: actual='missing'
        if actual!=expected: missing.append(f'{name}: {actual}; need {expected}')
    return missing

def validate_node(version):
    match=re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)',version.strip())
    if not match: raise LaunchError(f'Cannot read Node version: {version}')
    major,minor,_=map(int,match.groups())
    if not ((major==20 and minor>=19) or (major==22 and minor>=12) or major>=24):
        raise LaunchError('Node 20.19+, 22.12+, or 24+ is required. Install a supported Node LTS from https://nodejs.org/.')

def frontend_ready():
    # npm's hidden lock records its actual installed versions. Detect lock changes
    # without reinstalling on every launch, including an interrupted npm ci.
    try:
        wanted=json.loads((FRONTEND/'package-lock.json').read_text(encoding='utf-8'))['packages']
        installed=json.loads((FRONTEND/'node_modules'/'.package-lock.json').read_text(encoding='utf-8'))['packages']
        for key,data in wanted.items():
            if not key: continue
            if data.get('optional') and key not in installed: continue
            if installed.get(key,{}).get('version')!=data.get('version'): return False
        required=['vite/bin/vite.js','typescript/bin/tsc','react/package.json',
                  'react-dom/package.json','monaco-editor/package.json']
        return all((FRONTEND/'node_modules'/name).is_file() for name in required)
    except (OSError,KeyError,ValueError): return False

def fetch(url, *, json_body=True, timeout=2):
    with HTTP.open(url,timeout=timeout) as response:
        body=response.read(2_000_000).decode('utf-8')
        return json.loads(body) if json_body else body

def ollama_status():
    installed=shutil.which('ollama') is not None
    try:
        models=fetch('http://127.0.0.1:11434/api/tags').get('models',[])
        if any(m.get('name')==MODEL for m in models): return True,'Local Ollama and qwen3.5:4b are available.'
        return False,'Ollama is running, but qwen3.5:4b is missing. Run: ollama pull qwen3.5:4b'
    except (OSError,URLError,ValueError,AttributeError):
        return False,('Ollama is offline. Start the Ollama app or run ollama serve.' if installed else
                      'Ollama was not found. Install it from https://ollama.com/download/windows; then run ollama pull qwen3.5:4b.')

def port_busy(port):
    with socket.socket() as sock:
        sock.settimeout(.5)
        return sock.connect_ex(('127.0.0.1',port))==0

def backend_ready():
    try:
        payload=fetch('http://127.0.0.1:8000/api/bootstrap')
        return payload.get('model')==MODEL and payload.get('execution_enabled') is False and isinstance(payload.get('token'),str)
    except (OSError,ValueError,AttributeError): return False

def frontend_server_ready():
    try:
        html=fetch('http://127.0.0.1:5173/',json_body=False)
        return '/@vite/client' in html and '<title>AI Coding Mentor' in html
    except (OSError,ValueError): return False

def proxy_ready():
    try:
        return fetch('http://127.0.0.1:5173/api/bootstrap')['token']==fetch('http://127.0.0.1:8000/api/bootstrap')['token']
    except (OSError,ValueError,KeyError,TypeError): return False

def wait_ready(name, process, ready, log, timeout=45):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if process.poll() is not None: raise LaunchError(f'{name} exited ({process.returncode}). Read {log}')
        if ready(): return
        time.sleep(.2)
    raise LaunchError(f'{name} did not become ready within {timeout}s. Read {log}')

def stop_owned(process):
    import psutil
    # Capture descendants before terminating the root, and wait for all captured
    # processes. This supervisor cleanup is not a submitted-code sandbox.
    if process.poll() is not None: return
    try:
        parent=psutil.Process(process.pid)
        children=parent.children(recursive=True)
        for child in children:
            try: child.terminate()
            except psutil.NoSuchProcess: pass
        parent.terminate()
        _,alive=psutil.wait_procs([*children,parent],timeout=3)
        for child in alive:
            try: child.kill()
            except psutil.NoSuchProcess: pass
        psutil.wait_procs(alive,timeout=2)
        process.wait(timeout=3)
    except psutil.NoSuchProcess: pass

def supervise(node):
    owned=[];logs=[]
    try:
        for name,port,ready,command,cwd in [
            ('Backend',8000,backend_ready,[sys.executable,'-m','uvicorn','backend.api.app:app','--host','127.0.0.1','--port','8000'],ROOT),
            ('Frontend',5173,frontend_server_ready,[node,str(FRONTEND/'node_modules'/'vite'/'bin'/'vite.js'),'--host','127.0.0.1','--port','5173','--strictPort'],FRONTEND),
        ]:
            if port_busy(port):
                if not ready(): raise LaunchError(f'Port {port} is occupied by an unrecognized service. Close that service yourself; this launcher will not kill it.')
                print(f'{name}: reusing existing local mentor service on {port}.',flush=True)
                continue
            directory=ROOT/'.local-run'/'logs';directory.mkdir(parents=True,exist_ok=True)
            log=directory/f'{name.lower()}-{time.time_ns()}-{os.getpid()}.log'
            handle=log.open('w',encoding='utf-8');logs.append(handle)
            process=subprocess.Popen(command,cwd=cwd,stdout=handle,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            owned.append(process)
            wait_ready(name,process,ready,log)
            print(f'{name}: ready; log {log}',flush=True)
        if not proxy_ready(): raise LaunchError('Frontend API proxy does not match the backend. Restart the frontend from this project.')
        health=fetch('http://127.0.0.1:8000/api/health',timeout=8)
        if health.get('api')!='ready' or health.get('execution_enabled') is not False:
            raise LaunchError('Backend health response is unexpected; browser execution must remain disabled.')
        print('Open http://127.0.0.1:5173/\nRun is disabled until execution isolation is verified.',flush=True)
        if not owned:
            print('No new processes started. Existing services were left untouched.');return
        print('Keep this terminal open. Ctrl+C stops only services started by this launch.',flush=True)
        while True:
            if any(p.poll() is not None for p in owned): raise LaunchError('A managed service stopped. Inspect .local-run/logs and launch again.')
            time.sleep(.5)
    except KeyboardInterrupt:
        print('\nStopping services started by this launcher...',flush=True)
    finally:
        for process in reversed(owned): stop_owned(process)
        for handle in logs: handle.close()

def setup(node):
    venv=ROOT/'.venv';target=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if not target.is_file(): run([sys.executable,'-m','venv',str(venv)],timeout=90)
    # Probe using the selected environment, not the global interpreter.
    result=run([str(target),'-c',"import json; from scripts.start_dev import missing_python_packages; print(json.dumps(missing_python_packages()))"])
    if json.loads(result):
        print('Installing pinned backend dependencies into .venv...',flush=True)
        run([str(target),'-m','pip','install','-r',str(ROOT/'requirements-web.txt')],timeout=600)
    else: print('Backend dependencies already match; skipping pip install.')
    if not frontend_ready():
        print('Installing locked frontend dependencies...',flush=True)
        npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
        if os.name=='nt':
            cli=Path(npm).parent/'node_modules'/'npm'/'bin'/'npm-cli.js'
            if not cli.is_file(): raise LaunchError('Cannot locate npm-cli.js beside npm.cmd. Repair your Node LTS installation or run npm.cmd ci manually in frontend.')
            command=[node,str(cli),'ci','--cache','.npm-cache']
        else: command=[npm,'ci','--cache','.npm-cache']
        run(command,cwd=FRONTEND,timeout=600)
    else: print('Frontend dependencies already match; skipping npm ci.')
    print('Setup complete. Run .\\start.cmd (or python scripts/start_dev.py).')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--setup',action='store_true',help='Explicitly install/repair missing dependencies in .venv and node_modules')
    group.add_argument('--check',action='store_true',help='Check prerequisites without installing or starting services')
    parser.add_argument('--require-tutor',action='store_true',help='Fail rather than launch offline if Ollama/model is unavailable')
    args=parser.parse_args(argv)
    target=ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if target.is_file() and Path(sys.executable).resolve()!=target.resolve() and not args.setup:
        os.execv(str(target),[str(target),str(Path(__file__).resolve()),*(sys.argv[1:] if argv is None else argv)])
    try:
        if sys.version_info<(3,11): raise LaunchError('Python 3.11+ is required. Install Python and enable PATH.')
        node=shutil.which('node');npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
        if not node or not npm: raise LaunchError('Node.js/npm were not found. Install Node LTS from https://nodejs.org/ and reopen this terminal.')
        validate_node(run([node,'--version']))
        print(f'Python {sys.version.split()[0]}: {sys.executable}\nNode: {node}',flush=True)
        if args.setup: setup(node);return 0
        missing=missing_python_packages()
        if missing: raise LaunchError('Backend dependencies missing/mismatched: '+', '.join(missing)+'\nRun .\\start.cmd --setup')
        if not frontend_ready(): raise LaunchError('Frontend dependencies are missing or do not match package-lock.json. Run .\\start.cmd --setup')
        ready,message=ollama_status();print(('OK: ' if ready else 'WARNING: ')+message,flush=True)
        if not ready and args.require_tutor: raise LaunchError('AI tutor is required but unavailable. '+message)
        if not ready: print('Offline launch supports catalogue, authored lessons, drafts, and reference/mock results.')
        if args.check:
            for name,port,test in [('Backend',8000,backend_ready),('Frontend',5173,frontend_server_ready)]:
                if port_busy(port) and not test(): raise LaunchError(f'{name} port {port} is occupied by an unrecognized service.')
            print('Prerequisite check passed. No installations or service starts performed.');return 0
        supervise(node);return 0
    except (LaunchError,OSError,ValueError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr,flush=True);return 1

if __name__=='__main__': sys.exit(main())
