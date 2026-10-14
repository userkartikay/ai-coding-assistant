# Overhaul O1 — reliable launch and execution readiness

Date: 2026-10-13. The pasted request explicitly requires a stop after the first
major milestone. This increment implements launch reliability and investigates
execution readiness; it does not implement the whole overhaul.

## Changes

- `start.cmd`: single Windows command from the project directory, Python discovery,
  quoted project path support, actionable missing-Python message.
- `scripts/start_dev.py`: Python/Node checks, pinned backend and installed frontend
  dependency validation, optional explicit setup, model/daemon status, offline mode,
  fixed localhost servers, readiness/proxy/health checks, unique service logs,
  existing-service reuse, bounded startup, monitoring, and owned-process cleanup.
- `.gitignore`: local launch logs/state excluded from source artifacts.
- `tests/test_launcher.py`: 21 regression cases for supported/unsupported versions,
  package mismatch, missing/optional frontend files, exact model matching/offline
  status, no installation/start during check, explicit setup/skip behavior, unknown
  port ownership, reuse without spawn, failed-start cleanup, and real child-tree exit.
- `PLAN.md`, `PROGRESS.md`, `DECISIONS.md`: record O1 stop point, new staged order,
  launch design and candidate isolation gate. `docs/FRONTEND.md` points to the new
  preferred launch workflow while preserving manual commands.

No backend/frontend business behavior, catalogue identity, curriculum content,
reference fixture, learner database, draft key or model prompt was changed. No new
runtime dependency, elevated Windows operation, container start, OS policy change,
or automatic model download was introduced.

## Verified behavior

- Actual runtime: Python 3.11.6, Node 24.20.0, npm 11.7.0, Ollama 0.34.0.
- `start.cmd --check` succeeded without dependency installation or service starts.
- `start.cmd` started both services from free ports and printed ready only after
  frontend/backend/proxy/health checks. Repeating it reused both without duplicates.
- Actual terminal Ctrl+C printed owned-service cleanup; sockets 8000 and 5173 then
  refused connections. Windows' ordinary batch-termination prompt followed cleanup.
  A fresh `start.cmd` started both again for handoff.
- Restarted frontend returned HTTP 200; proxy returned all 133 questions with the
  original 10 verified fixtures. Backend reported tutor available and execution
  disabled. Qwen availability was checked via tags/health, not a teaching evaluation.
- Fresh-environment downloads were not performed. Explicit setup logic and skipping
  already matching dependencies were tested with controlled temporary fixtures.
  Actual installed dependencies passed the normal launch checks.

The initial integrated suite passed 177 tests; an additional explicit-setup regression
was added afterward and the final focused launcher run passed 21 tests. Final
integrated results are recorded below after completion, not inferred from counts.

### Final verification

- Final complete Python suite: **178 passed, zero skipped, 142.96 seconds**.
  Two existing Starlette/httpx/anyio dependency warnings remain unsuppressed.
- Final focused launcher suite: **21 passed, 0.85 seconds**.
- Real Windows launch/check/reuse/shutdown/restart and HTTP/proxy/health checks
  passed. Both services are running through the new launcher for handoff.
- Frontend source/dependencies were unchanged; frontend lint/build/Vitest were not
  rerun for this launcher-only increment. Runtime serving/proxy were checked.
- No fresh dependency downloads, isolation penetration tests, RAM/latency benchmark,
  or new teaching-quality evaluation was performed. Those are not claimed complete.

## Execution assessment and remaining limitations

See [EXECUTION_READINESS.md](EXECUTION_READINESS.md) for the options/security/overhead/
complexity comparison and primary sources. WSL2 Ubuntu and docker-desktop are
installed and stopped. Docker CLI is present but its Linux daemon is unavailable.

Recommended O2 candidate: native AppContainer/LPAC resource isolation plus kernel
Job quotas, verified for compilation as well as runtime. This has not been built
or security-tested. Ordinary WSL, timeouts, soft memory polling, directories and
localhost binding do not establish the required boundary. No honest measured
RAM/startup comparison is possible before prototyping. A separately managed VM is
the fallback if native isolation cannot be made reliable.

Run/Submit remain disabled. The local runner remains limited to explicitly trusted
code. Existing Qwen factual/teaching limitations remain unchanged; startup health
is not proof of tutoring correctness. Lessons/cards, 40–50 fixtures, drills/traces,
learning-history integration and revision are subsequent milestones, not done here.

## Handoff

```powershell
# From C:\Users\karti\OneDrive\Desktop\dsa learning project
.\start.cmd
```

Open http://127.0.0.1:5173/. For first setup/repair: `start.cmd --setup`. Diagnostics:
`start.cmd --check`. Full commands, offline behavior and troubleshooting:
[LAUNCH.md](LAUNCH.md).

Stop after O1 and review this report before O2. No additional milestone was started.
