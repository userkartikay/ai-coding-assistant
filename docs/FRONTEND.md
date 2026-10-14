# Frontend MVP — local launch and verification

The user authorized this frontend-first increment ahead of completing Milestone 2.2.
The original MVP was followed by the user-authorized curriculum/learning increment.
Current features and checks are in LEARNING_EXPANSION.md; launch commands below still apply.

## Launch

Preferred Windows workflow is now `start.cmd`; see [LAUNCH.md](LAUNCH.md) for the
single-command launch, explicit setup, diagnostics, offline mode and shutdown.
The manual two-terminal commands below remain valid.

From the repository root in PowerShell, start the API in one terminal:

```powershell
python -m pip install -r requirements-web.txt
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd frontend
npm.cmd ci --cache .npm-cache
npm.cmd run dev
```

Open http://127.0.0.1:5173. Vite proxies /api to the local backend; the browser does
not call Ollama. Keep Ollama running with qwen3.5:4b for AI hints. Without Ollama,
question browsing, drafts, themes, and reference/mock result viewing remain usable.
Both servers were left running for the handoff. Ctrl+C stops each server.

For a built frontend without Vite:

```powershell
cd frontend
npm.cmd run build
cd ..
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Build before starting the API so its static mount sees
the bundle. Drafts belong to the browser origin: ports 5173 and 8000 have separate
storage. Use Download C++ draft when moving drafts between browsers/origins.

Tested tools: Node 24.20.0, npm 11.7.0, Python 3.11; exact frontend versions are in
package-lock.json. Python adapter dependencies are pinned in requirements-web.txt.
No database initialization, migration, cloud account, or paid service is required.

## Functional features

- All 133 registry questions, official-number/title/pattern/subpattern search, numeric/
  difficulty/topic sorting, and explicit 10 verified-suite / 123 catalogue-only status.
- Pattern/subpattern filters and original teaching metadata in Guided Learning.
  Independent Practice defaults on every load and hides those metadata clues.
- Original stored summaries/constraints and examples for executable questions.
  Catalogue-only questions state that missing content is unavailable. Original
  problem links are preserved; no new statements or metadata were invented.
- Locally bundled Monaco C++ grammar/worker, verified starter signatures, readable
  editor, themes, keyboard-accessible panel split, and editor-height adjustment.
- Per-question auto-saved drafts, Ctrl+S/Save draft, storage-failure alerts, and file
  download. No draft is sent to a compiler. Optional, explicitly requested solution review sends
  the draft snapshot through the backend to local Ollama.
- Dedicated collapsible mentor panel with five backend-gated levels, complete-output
  validation, elapsed waiting time, failure/retry, session restoration, and explicit
  acknowledgement before requesting the complete solution.
- Collapse/expand result sections, actual canonical/known-bug reference reports,
  individual failed cases with input/expected/actual output, compiler diagnostics
  through a labeled mock display, and careful AC wording.
- Responsive desktop/mobile layouts, skip link, labeled controls, focus treatment,
  and light/dark themes. No external font, CDN editor, or gratuitous animation.

## Backend adapter and safety

backend/api/app.py uses the existing registry and SocraticCliApp; hint schemas,
progressive rules, prompts, recovery, and judge behavior are not reimplemented in
React. Sessions are ephemeral (100 maximum, two-hour idle expiry), not a replacement
for SQLite. The API serializes model calls and caches validated hints by tier.

The API is bound to 127.0.0.1 with exact local origins, Host checks, and an ephemeral
local bootstrap token for session operations. Those measures are not an untrusted
execution sandbox or authentication against other local programs. Do not bind this
MVP to 0.0.0.0 or deploy it as a public service.

There is NO execution endpoint, browser-controlled trusted flag, or automatic
student/model-code compilation. The protected review endpoint accepts a bounded
source snapshot solely for static AI analysis; it never invokes the runner. Run is visibly disabled. The
optional mock preview is explicitly not a correctness result. Reference evidence
belongs to repository-authored trusted fixtures, never to the draft in the editor.

scripts/export_reference_results.py was manually executed using explicit trusted
acknowledgement on 20 repository fixtures (10 canonical, 10 known bugs). It produced
docs/REFERENCE_RESULTS.json; all canonical cases passed and all known bugs failed.
Routes only read this file. Fingerprints and schema checks reject stale/corrupt
reports. Large I/O fields are labeled excerpts. Regenerate after fixture changes:

```powershell
python scripts/export_reference_results.py
```

This command requires MinGW g++, and must remain a manual trusted-local command.
Neither question browsing nor reference viewing triggers compilation.

## Historical frontend MVP checks (current checks in LEARNING_EXPANSION.md)

- Frontend TypeScript + Vite production build: PASS.
- ESLint, zero-warning policy: PASS.
- Vitest DOM interaction/storage tests: 12 passed.
- New adapter tests: 15 passed. Cover metadata fidelity, missing statements, origin/
  Host/token protections, no execution route, body rejection, tier gating/cache,
  failed-generation state, expiry/capacity, mock labels, stale references, and model
  request serialization. Fake tutor only for these isolated tests.
- Complete Python suite: 128 passed, zero skipped, 157.89 seconds. Includes existing
  live Ollama and trusted MinGW tests. Two dependency deprecation warnings remain
  in Starlette TestClient (httpx/anyio); they are not suppressed.
- npm production audit after patched DOMPurify 3.4.17 override: zero advisories.
- Final restarted services: built frontend HTML/JavaScript on port 8000 returned 200;
  Vite /api proxy returned 53 questions with 10 executable entries.
- Browser console contained no captured errors/warnings during the verified editor flow.
- Build retains Monaco's lazy editor size warning (~696 KiB gzip), rather than
  suppressing it. The main application bundle is ~78 KiB gzip. Editor resources are
  served locally and loaded only for the workspace.

Browser verification used the real local app, not the mocked editor:

- Actual Monaco loaded with C++ coloring; edited and saved a disposable comment,
  switched to a catalogue-only question, and restored the original draft.
- Guided pattern filter plus title search found Merge Intervals; the UI displayed
  missing statement and unavailable grounded tutoring. Returning to Independent
  mode removed teaching filters/metadata.
- Live Qwen Level 1 request displayed waiting state, then validated guidance and
  1/5 unlocked. Level 2 became available only after server success.
- Reference AC showed 5/5 available tests; known-bug WA showed 3/5; mock compiler
  failure displayed explicit illustrative diagnostics. None executed the draft.
- Light/dark theme controls, keyboard panel resizing (41 -> 39), editor height
  adjustment (340 -> 360), and the 390px mobile breakpoint were checked. No
  horizontal overflow was observed at that mobile size.

## Known limits and next milestone

- No arbitrary code execution until meaningful isolation is verified. Host runner
  restrictions and soft resource safeguards remain exactly as documented previously.
- Tutor output is batched; no validated token-stream API exists. Progress is elapsed
  time, not fake streaming or percentage completion. AI advice still needs review.
- Hints are grounded to stored problem content; unrestricted free-form chat remains pending. Optional static draft review is now
  available for the ten grounded executable questions and is explicitly experimental. No claims of educational correctness are made.
- One hundred twenty-three questions remain catalogue-only. Their missing content is not fabricated.
- Drafts are browser-origin storage, not SQLite-backed or synchronized. Mentor session
  state resets after server restart/expiry; UI retry starts again from tier 1.
- Monaco provides syntax highlighting here, not a C++ compiler or language server.
- Reference verdicts are snapshots for trusted fixtures, not results of a submission.
- Full attempt/diagnosis persistence, summaries, revision, and analytics remain pending.

Screenshot: frontend-mvp.jpg. The localhost frontend tab was left open for testing.

Stop for user testing after the authorized learning increment. After feedback, the recommended next milestone is 2.2:
connect real practice sessions and available learning events to the existing SQLite
repository. Isolated execution is a separate safety prerequisite before enabling
student Run. Do not add other phases automatically during this handoff.

## Implementation references

[Vite guide](https://vite.dev/guide/),
[Monaco ESM integration](https://github.com/microsoft/monaco-editor/blob/main/docs/integrate-esm.md),
[FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/).
Monaco 0.57.0's installed public exports were inspected for its changed module paths;
the code uses the editor API and C++ grammar directly, not a CDN loader.
