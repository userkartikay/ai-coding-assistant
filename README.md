# AI Coding Mentor

A local-first DSA practice application focused on independent problem solving and
Socratic teaching. React, TypeScript, Vite and Monaco connect to FastAPI, SQLite
infrastructure and local Qwen 3.5 4B through direct Ollama integration.

## Current features

- 133 questions identified by official LeetCode numbers; 10 verified executable
  reference fixtures and 123 catalogue-only entries.
- Search, difficulty/topic sorting, independent and guided practice modes.
- C++ editor with local draft restoration, responsive panels and themes.
- Five progressively gated hint levels; optional experimental approach review and
  alternative comparison.
- 16 authored starter lessons, subpattern distinctions, deterministic walkthrough
  states and links to practice.
- Reference/mock judge reports, clearly separated from AI advice and student drafts.

## Run on Windows

Install Python 3.11+ and a supported Node LTS (Node 24 tested). Clone the repository:

```powershell
git clone https://github.com/userkartikay/ai-coding-assistant.git
cd ai-coding-assistant
.\start.cmd --setup
.\start.cmd
```

Open http://127.0.0.1:5173/. Subsequent launches need only `start.cmd`; dependency
installation is explicit. `start.cmd --check` performs read-only diagnostics.
Ctrl+C stops services started by the launcher. See [launch instructions](docs/LAUNCH.md).

For AI features, install [Ollama](https://ollama.com/download/windows), keep it running,
and install the model separately:

```powershell
ollama pull qwen3.5:4b
```

Browsing, authored lessons, drafts and reference reports remain usable offline.

## Execution and teaching limitations

**Browser Run/Submit is disabled.** The Windows C++ runner executes with host
privileges and accepts only explicitly trusted local code. Timeouts/output limits
are resource safeguards, not a secure sandbox. No API endpoint executes submissions.
Keep the application bound to localhost; it is not ready for public hosting.

AI feedback is experimental: Qwen can miss known bugs or misstate algorithmic facts.
Structural validation is not proof of correctness or teaching quality. Reference
verdicts describe repository fixtures, never the current student draft. AC means
passing the available verified suite, not universal correctness.

SQLite integration, revision scheduling and independently verified code isolation
remain unfinished. See [current progress](PROGRESS.md), [roadmap](PLAN.md),
[architectural decisions](DECISIONS.md), and [execution assessment](docs/EXECUTION_READINESS.md).

## Development checks

```powershell
# Activate .venv first, or use .venv\Scripts\python.exe directly.
python -m pip install -r requirements-dev.txt
python -m pytest -q
cd frontend
npm.cmd test
npm.cmd run lint
npm.cmd run build
```

The complete Python suite includes live local Ollama checks and explicitly trusted
repository-authored C++ fixtures; it requires Qwen and MinGW g++. Launcher checks
can run separately with `python -m pytest tests/test_launcher.py -q`.
Historical verification results and their limits are recorded in the docs; do not
assume those results prove a fresh machine is configured correctly.

Dependencies, builds, runtime logs, environments and learner databases are excluded
from Git. No model weights or local learner records are included in this repository.
