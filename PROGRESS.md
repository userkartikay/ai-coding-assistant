# Project Progress Tracker

## GitHub publication — 2026-10-14

User authorized preparing and pushing the existing project to
https://github.com/userkartikay/ai-coding-assistant.git. Added README.md, pinned
requirements-dev.txt, portable line-ending rules, and exclusions for local secrets,
databases, runtime logs, dependencies, environments, and generated artifacts.
Credential-pattern and staged-artifact checks found no matches; 31 focused launcher/
catalogue tests passed. Application behavior and the O1 stop point remain unchanged.
The complete suite's last executed result remains 178 passed as recorded below.

## Current milestone — O1 reliable launch and execution readiness

The core-learning overhaul request explicitly says to stop after its first major
milestone. This increment implements launch reliability and an execution-readiness
assessment only; the prior curriculum/learning increment below is historical.

- `start.cmd` is the Windows entry point; `scripts/start_dev.py` checks Python/Node,
  pinned backend dependencies, installed frontend lock/files, Ollama/model tags,
  ports, server readiness, proxy matching and backend health.
- Ordinary launch/check never installs dependencies. Explicit `--setup` prefers a
  project venv and installs only missing/mismatched dependencies. Offline launch
  remains useful; `--require-tutor` requires the model. No admin requests, OS setting
  changes, Docker/WSL starts, database seeds, catalogue edits, or new dependencies.
- Child services bind to 127.0.0.1 on fixed ports. Unique logs, bounded startup,
  failure cleanup, monitored services, and Ctrl+C cleanup apply only to processes
  this invocation started. Recognized existing services are reused; unknown port
  owners are not killed.
- Real launch from free ports, reuse without duplicates, read-only checks, and
  Ctrl+C cleanup of both ports were verified. Python 3.11.6, Node 24.20.0, npm 11.7.0,
  Ollama 0.34.0 and qwen3.5:4b are present. Fresh-environment package downloads were
  not performed; setup decisions are regression-tested and existing dependency
  checks passed. The current services were restarted through the launcher.
- WSL lists Ubuntu/docker-desktop, both WSL2 and stopped; Docker CLI exists but its
  daemon is offline. No sandbox exists. Native AppContainer/LPAC plus Job limits is
  the recommended candidate for O2, not a verified boundary. Run/Submit stay disabled.

Final checks: 178 Python tests passed (142.96 s, two existing dependency warnings),
including 21 launcher tests. Actual launch/check/reuse/Ctrl+C/restart and HTTP/proxy/
model health passed. Frontend source was unchanged; frontend lint/build/Vitest were
not rerun for this increment. Fresh dependency downloads and isolation tests are pending.

Checks/results: docs/OVERHAUL_O1.md. Launch: docs/LAUNCH.md. Isolation assessment:
docs/EXECUTION_READINESS.md. Stop here before implementing O2 or any learning overhaul.

## Historical phase — curriculum and learning experience expansion

User-authorized extension of 2.1, 3.1, and new frontend Milestone 4.4 before the
remaining 2.2 integration. The prior frontend-only handoff below is historical.

- 133 official LeetCode identities: original 53 records preserved exactly; 80 new
  catalogue-only entries. 10 executable fixtures and their reference fingerprints
  remain unchanged. Official number/title/URL/difficulty verification is recorded
  in docs/LEETCODE_IDENTITIES.json; it is not execution verification.
- Consistent `#number — title` in browser, practice, lesson links, and CLI. Search
  by number/title/pattern/subpattern; numeric, difficulty, and topic sorting.
  No existing internal ID, draft key, learning record, or real database was changed.
- 16 reviewed starter lessons with 50 subpattern distinctions, STL snippets,
  templates, complexity assumptions, recognition questions, mistakes, walkthrough
  controls, and related practice links. Lessons are optional.
- Hint Only retains existing progressive tiers. Approach review/comparison require
  explicit teaching-detail consent and analyse snapshots without execution.
  Generated advice is labeled separately from reference/mock verdicts. Review
  remains unavailable for questions without verified statement grounding.
- Grounded lesson follow-ups use the selected material; no retrieval infrastructure.
  One API model call at a time; schema validation, bounded recovery, size/context
  checks, and error/retry states reuse the existing Ollama client.
- Live testing found an Ollama grammar parser failure on lesson string length
  constraints. Sampler grammar omits only those bounds; complete Pydantic length,
  enum, and identity checks remain enforced. Regression tests retain those limits.
- Milestone 2.2, persistent summaries/revision scheduling, and execution isolation
  are still pending. Run remains disabled; localhost is not a sandbox.

Final verification: 157 Python tests passed (144.68 s, two dependency warnings),
26 frontend tests passed; lint and production build passed. Official-source recheck
matched all 133 identities. Five corrected-path model samples and one final bug probe
passed structure, but subjective review found serious factual limitations, including
a missed known bug. Structural success is not teaching correctness.

Verification results and teaching-quality limitations: docs/LEARNING_EXPANSION.md
and docs/LEARNING_EVALUATION.json. Real browser checks covered official search,
walkthrough/practice links, draft restoration, review consent, responsive layout,
and a successful local Qwen lesson request after stale-token retry. No console
errors/warnings captured. Both services are running; stop for hands-on testing now.

## Historical frontend MVP handoff

Frontend MVP (Phase 4 with a minimum Phase 3 adapter), explicitly prioritized by the
user before completion of Milestone 2.2. The two-hour scope was clarified as option 1:
finish the usable MVP and stop for hands-on testing. Keep phase identifiers, but
follow the authorized frontend-first execution order in PLAN.md.

Milestone 2.2 persistence integration and 2.3 taxonomy remain unfinished. No arbitrary
HTTP execution, analytics, revision scheduler, RAG, orchestration, or voice was added.

## Frontend MVP completed

- React/TypeScript/Vite, local Monaco C++ grammar/worker, verified starter signatures.
- Original 53-question registry browser, difficulty/search and guided pattern/subpattern
  filters; 10 verified-suite entries are distinct from 43 catalogue-only entries.
- Independent Practice is the default. Missing statements/constraints/signatures are
  explicit; no metadata or problem content was fabricated.
- Draft auto-save/restore per question, Ctrl+S/Save, download, visible storage errors.
- Resizable problem/editor split and editor height, collapsible mentor/results,
  responsive layouts, light/dark themes, labeled keyboard-accessible controls.
- Thin localhost FastAPI adapter reuses existing hint logic and validation. All five
  tiers are available for executable questions, with failure/retry, elapsed waiting,
  cache/restoration, and explicit solution acknowledgement. No direct browser Ollama.
- API has bounded ephemeral sessions, one active model request, exact local origins,
  Host checks and a local bootstrap token. No code execution route exists.
- Manual trusted export produced real canonical/known-bug reports for all 10 fixtures.
  Browser views reference evidence plus separately labeled mock error previews.
  Neither compiles the current draft; Run stays disabled pending verified isolation.
- Patched DOMPurify dependency override; npm production audit reports zero advisories.

### Frontend verification

- TypeScript/Vite production build and ESLint: passed. Monaco's lazy bundle size
  warning remains visible (~696 KiB gzip); it is served locally.
- Vitest UI/storage tests: 12 passed.
- New API adapter tests: 15 passed (fake tutor, no arbitrary execution).
- Complete Python suite: 128 passed, zero skipped, 157.89 s. Two Starlette test-client
  dependency deprecation warnings remain; no tests were weakened or warnings hidden.
- Manual actual-browser verification: Monaco edit/save/restore, guided filters,
  catalogue-only states, live Qwen Level 1 waiting -> validated hint -> tier unlock,
  canonical AC/known-bug WA/mock compiler diagnostics, themes, keyboard resize, and
  390px responsive layout without horizontal overflow.

Launch and full limitations: docs/FRONTEND.md. Both localhost services were started
for handoff. The browser MVP stops here for user testing; persistent events and
remaining phases are not silently implemented.

## Completed remediation

- SQLite ON CONFLICT updates preserve referenced rows and solved flags. Savepoint
  rollback prevents partial attempts and partial seeds; newest-first queries use IDs
  to break timestamp ties.
- Additive v1 schema migration adds practice sessions; old attempt-associated hints
  remain readable. Legacy problem identities consolidate transactionally with original
  metadata archived. No real learner database was touched during remediation.
- 53 stable LeetCode identities: 10 executable fixtures and 43 catalogue-only entries.
  Original curated metadata/provenance is retained through the registry.
- Explicit function signatures fix helper-signature display. Problem selection and
  statements do not intentionally disclose patterns before hints.
- Boundary and maximum-input cases cover all ten fixtures. Climbing Stairs n=1 and
  n=45 are checked. Iterative Islands and depth-first tree references avoid Windows
  stack overflow at documented limits. Empty suites are rejected.
- AC explicitly means passing the available verified suite, not universal correctness.
- Per-pipe output limits apply while running, including compiler stderr. Watchdog
  tracks observed children, terminates and waits, and uses sampled RSS budgets.
- Compilation/execution require explicit trusted acknowledgement. CLI submission is
  disabled unless launched with --trusted-local. No untrusted execution is supported.
- Backend hint transitions are sequential and advance only on successful validation
  and optional persistence. Fixed Level 1 failure guidance reveals no pattern and
  does not unlock a tier; failures at higher tiers are explicit.
- JSON-schema-constrained Ollama generation has per-tier budgets, separate L4/L5
  fields, completion/truncation checks, and at most two sequential attempts. Thinking
  is never treated as the answer. Conservative context budget uses 4K normally, at
  most 8K, or rejects the input. Small Tutor protocol supports alternate providers.
- Level 2 guidance rejects the reproduced conditional pointer-rule disclosure.
  This heuristic does not prove absence of every semantic leak.
- Teaching evaluation covers all five levels and all diagnosis fields. Exact output
  hashes link separately scored factual correctness and teaching usefulness reviews;
  every reviewer identifies whether it is human or AI. Structural success alone is
  never reported as educational correctness.
- Benchmark utilities distinguish raw response chunks, validated completion, and
  native token counts; old measurements are annotated as historical evidence.

## Verification executed

- Original audit baseline: 62 passed, zero skipped, 238.50 seconds.
- Eleven newly written audit regressions: all 11 FAILED on the original implementation.
- First corrected data/tutor-boundary check: 32 passed, 4.14 seconds.
- Focused persistence, execution, and expanded fixtures: 43 passed, 51.57 seconds.
- Focused tutor validation/recovery and audit regressions: 29 passed, 1.69 seconds.
- Offline evaluator/CLI check: 7 passed, 2 live tests deselected, 8.96 seconds.
- First integrated suite: 110 passed, zero skipped, 223.34 seconds.
- Additional focused checks after refinements: 38 passed, 4.01 seconds; benchmark and
  tier checks: 21 passed, 1.25 seconds.
- Final integrated suite: **113 passed, zero skipped, 138.20 seconds**. Includes existing live Ollama tests and trusted MinGW fixtures after all corrections.

Host access is necessary for MinGW and localhost Ollama on this machine. Tests use
trusted fixtures, in-memory or temporary SQLite databases, and temporary executables.
The test infrastructure does not run arbitrary student/model code.

## Before / after evidence

- Identical problem upsert: deleted attempts/hints/diagnoses -> history retained.
- Same-second attempts: oldest first -> descending attempt ID.
- Seed: 63 rows with ten duplicate titles -> 53 unique identities, including legacy
  history remapping and original metadata preservation.
- First-submission hint association: impossible with attempt-only FK -> session hints
  recorded with zero attempts; optional attempts can reference that session.
- Failed result insertion: partial attempt could survive -> savepoint removes it.
- Empty suite: AC -> configuration error before compilation.
- Incorrect Climbing Stairs n=1: AC -> WA at the added boundary case.
- Islands 300x300 all land: old recursion exits 3221225725 (0xC00000FD Windows stack
  overflow) under the corrected process runner -> iterative reference AC at the same
  two-second limit. Original runner had reported TLE while the fault dialog waited.
- Islands CLI signature: helper dfs -> required numIslands signature.
- Wrong-tier/code-bearing L1 and direct L5 unlock: accepted -> validation/gating rejects.
- Failed L1 generation: pattern leaked and state advanced -> neutral fallback, unchanged state.
- Live L4/L5: malformed/truncated JSON in audit -> valid separate fields for the tested
  Two Sum II sample. Retries remain bounded; broader quality is not established.
- Streaming benchmark: thinking counted as first hint and chunks as tokens -> ignored
  thinking, separate validated-hint time, and Ollama eval_count.

## Teaching evaluation scope

One fixed Two Sum II misconception was evaluated sequentially against local
qwen3.5:4b (Q4_K_M). All five tiers were structurally valid and the diagnosis category
matched. Live review found L2 over-disclosure; initial output is preserved in
INITIAL_REMEDIATION_EVALUATION.json and a regression/prompt correction was added.
Final output and review scope are recorded in REMEDIATION_EVALUATION.json. Six subjective AI reviews scored factual correctness 1.33/2 and teaching usefulness 1.50/2; these are not human ratings or curriculum-wide conclusions.

This is not a comprehensive 10-problem, five-tier pedagogical certification. No
human learning-outcome study or human quality rating has been performed. Generated
C++ was not automatically executed. See the review evidence for remaining issues.

## Remaining safety and teaching limitations

- Trusted local execution has full host privileges. Soft 20 ms RSS sampling and
  observed-process cleanup can miss transient allocations or escaping descendants.
  Temp cleanup remains best-effort, not guaranteed. Secure isolation remains 5.1.
- No arbitrary execution may be added to HTTP endpoints before isolation is verified.
- Schema checks and leakage heuristics cannot prove factual/educational correctness.
  Hint usefulness, invariant explanations, and misleading examples still need review.
- Input rejection is conservative and may refuse long submissions; there is no
  context summarization or RAG. Optional reflection helpers remain outside this
  remediation's evaluation scope.
- No guaranteed inference speed, offload percentage, or two-second usable hint target.
- CLI has optional session/hint association only. Complete attempt/diagnosis persistence,
  summaries, and revision behavior remain unfinished Milestone 2.2 and later work.

## Architectural decisions

DECISIONS.md records Decisions 9-15: plain SQLite/savepoints, stable identities,
practice sessions, trusted process safeguards, bounded structured generation,
constraint-aware judging, and separate teaching-quality review.

## Immediate next task

User hands-on testing of the frontend MVP. Stop here. After feedback, resume 2.2:
connect practice learning events and summaries to the existing SQLite layer. Do not
enable arbitrary browser execution before verified isolation. Any remaining Phase
3/4 streaming/debugging work is separate from this delivered MVP.
