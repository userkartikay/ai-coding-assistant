# Windows local launch — Overhaul milestone O1

From the project folder in a normal PowerShell terminal:

```powershell
.\start.cmd
```

Open http://127.0.0.1:5173/. Keep the terminal open; Ctrl+C stops only the backend
and frontend started by this invocation. If Windows then asks `Terminate batch job
(Y/N)?`, type `Y`; service cleanup has already run. Existing recognized mentor
services are reused and left running. If both were already running, the command exits after
checking them. It never kills an unknown port owner. No administrator terminal,
execution-policy change, Docker, WSL, or C++ compiler is required for this milestone.

## First setup or dependency repair

Prerequisites: Python 3.11+, supported Node (20.19+, 22.12+, or 24+; Node 24 LTS is
the tested version), and npm. Install from official Python/Node installers and
enable PATH, then reopen your terminal. AI features additionally need local Ollama.

```powershell
.\start.cmd --setup
ollama pull qwen3.5:4b
.\start.cmd
```

`--setup` explicitly creates a project `.venv` if missing, installs pinned Python
requirements only when missing/mismatched in that environment, and runs `npm ci`
only when the installed frontend lock/dependencies are missing/mismatched. Setup
requires Internet access for missing packages. It does not download the model or
start/change Ollama, Docker, WSL, Windows features, or any database. It never removes
learner history or draft storage. Normal launch/check has no dependency installation.

If a `.venv` already exists, launch prefers its Python. An existing valid global
Python installation works without setup, as on the verified development machine.

## Diagnostics and offline mode

```powershell
.\start.cmd --check
.\start.cmd --require-tutor
```

`--check` verifies runtime versions, exact pinned backend versions, frontend lock
versions and essential installed files, Ollama tags/model availability, and occupied
ports. It starts nothing and installs nothing. It does not test teaching correctness.
`--require-tutor` fails if Ollama/model is unavailable; by default that is a warning
and offline catalogue, authored lessons, drafts and reference/mock results still work.
Start the Ollama app, or run `ollama serve` separately if it is not already serving.

Backend starts at 127.0.0.1:8000, Vite at 127.0.0.1:5173 with strict port selection.
Readiness checks the backend bootstrap, frontend HTML, matching Vite API proxy, and
backend health. Loopback probes bypass environment HTTP proxies. Bootstrap matching
helps identify accidentally reused services; it is not a sandbox or authentication
against other local programs.

Managed service output is saved to unique `.local-run/logs/*.log` files. Startup
failure names the log to inspect and cleans up other processes started by the same
invocation. The existing Windows host runner stays trusted-only; Run remains disabled.

## Troubleshooting

- **Python not found / Store alias:** install Python from python.org with PATH, or
  invoke `py -3 scripts/start_dev.py`. The launcher reports a missing/invalid runtime.
- **Node/npm missing:** install Node LTS and reopen PowerShell. If npm's CLI cannot
  be located during setup, repair Node or run `npm.cmd ci` manually in `frontend`.
- **Dependencies missing/stale:** use `start.cmd --setup`; the selected interpreter
  and any mismatched Python packages are printed. No silent global pip repair.
- **Port 8000/5173 occupied:** close the identified service in its own terminal.
  The launcher does not terminate unrelated processes or move to a different port.
- **Ollama offline/model missing:** follow the printed serve/pull command. CPU/GPU
  inference is not warmed up or generated during prerequisite checks.
- **Backend code changed:** stop the owning launcher and start again. Vite reloads
  frontend changes; the backend deliberately has no background reload supervisor.
- **Abruptly closing the terminal:** prefer Ctrl+C and wait for cleanup. Process
  cleanup is best effort if Windows forcibly terminates the launcher; relaunch
  recognizes surviving services. It is not execution containment.

Manual two-terminal commands in FRONTEND.md remain supported. Do not bind either
server to 0.0.0.0 or expose the app publicly.
