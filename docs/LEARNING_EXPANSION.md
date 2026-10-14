# Curriculum and learning handoff — 2026-10-13

## Implemented scope

The user authorized this increment before the remaining Milestone 2.2 work.
The catalogue contains **133 questions: 80 additions, 10 verified executable
fixtures, 123 catalogue-only entries**. All original 53 source records remain
exactly unchanged, including curated metadata and provenance. The actual learner
database was not modified. Existing `lc_<official number>` IDs, aliases, reference
fingerprints, browser draft keys, and historical references remain compatible.

Official number/title/URL/difficulty mappings were checked against
[LeetCode's public catalogue](https://leetcode.com/api/problems/all/).
`LEETCODE_IDENTITIES.json` records all mappings; `original-catalogue-53.json`
captures the preservation baseline. Recheck without writing learner data:

```powershell
python -m scripts.verify_leetcode_identities
```

Display uses `#167 — Two Sum II - Input Array Is Sorted` consistently in the
question browser, practice heading, lesson links, and CLI. Menu choices in the CLI
are explicitly choices, not invented problem numbers. Search supports official
number (including `#`), title, pattern, and subpattern. Sorting uses numeric
LeetCode order, Easy/Medium/Hard order, or alphabetical topic with numeric ties.
Independent Practice still hides initial pattern/complexity labels; deliberate
topic search is supported without automatically switching practice mode.

The additions use original concise editorial summaries and topic-specific
prerequisites/objectives. Numeric constraints, verified signatures, test cases,
and executable status were not invented. Existing missing content remains explicit.
All additions are catalogue-only. Metadata verification does not establish an
execution harness or prove editorial content correct. New future local identities
have a separate source ID and cannot assign a fake LeetCode number.

See `CURRICULUM_EXPANSION.md` for all 133 question/subpattern mappings and coverage.
Sixteen teaching families cover every catalogue primary-pattern label exactly once.

## Learning experience

Learn DSA includes **16 authored starter lessons and 50 subpattern distinctions**:
arrays/hashing, two pointers, sliding windows, binary search, prefix sums, strings,
stacks/queues, linked lists, trees/BST, graphs, DP, greedy/intervals, heaps,
backtracking, tries, and bits. Each has introduction, intuition, STL snippets,
one reusable template with assumptions, complexity notes, recognition questions,
misconceptions/edges, an annotated walkthrough, and officially numbered practice
links. These are starter lessons reviewed by Codex, not a completed expert-reviewed
course. Templates illustrate subpatterns and may use explicitly named placeholder
node types; they are not promised drop-in LeetCode solutions.

Walkthrough controls navigate fixed reviewed states. Array/window/binary-search/DP
states, stack push/pop, and linked-node/tree/graph diagrams are local React/SVG
views. They do not execute user input or simulate arbitrary algorithms. Learning
is optional. Linked practice retains the selected practice mode, and draft storage
restores the same question key after learning navigation.

Grounded lesson follow-ups send selected material and the student's question to
local Ollama through FastAPI. Responses identify material sections and remain
labeled AI follow-ups, separate from authored material.

## Optional solution review

Hint Only preserves the existing five-tier backend gate. Review My Approach and
Compare Alternative Solutions require explicit consent to reveal teaching details
and send the draft snapshot to local Ollama. Review currently works only for the
ten questions with verified statement grounding. Catalogue-only review remains
clearly unavailable. The source is bounded to 3,500 characters and the existing
8K context ceiling can reject inputs earlier when combined context is too large.

Structured review includes inferred pattern, invariant, estimated complexity,
observations, edge cases, simplification, uncertainty, guiding question, and
comparison alternatives with individual complexity/tradeoffs. It never unlocks
hints, compiles code, records AC, or treats trusted fixture results as evidence
about the draft. Edits mark earlier feedback as an earlier snapshot; Revise this
draft returns focus to the editor. Requests share the existing API model lock.
Failures show retry states without fabricated feedback.

Review is **experimental**. It can miss known bugs and invent concerns. Schema
validation does not make analysis educationally correct. Do not use it to certify
solutions or replace manual tracing and verified tests.

## Live Qwen evaluation, separately from automated tests

`LEARNING_EVALUATION_INITIAL.json` preserves the initial five samples: 2/5 structural
successes, one invalid review, and two lesson HTTP 400 grammar failures. An initial
valid binary-search review still invented an overflow concern and excessive certainty.

The installed Ollama grammar parser rejected lesson string length constraints.
A diagnostic sampler request succeeded with those generation-only bounds omitted.
The final lesson path retains the complete original Pydantic length limits, section
enums, and lesson identity validation. Invalid short/long/unknown-section outputs
still fail regression tests. Other response schemas retain native constraints.

After the compatibility correction and concise-review/recovery changes, five
repeat samples passed structural validation: three reviews and two lesson answers.
Latencies were **32.61, 45.89, 128.00, 87.21, and 55.23 seconds**. Calls were sequential
on local Qwen 3.5 4B. Raw responses and generation telemetry are preserved in
`LEARNING_EVALUATION.json`; comparison required bounded recovery.

Separate Codex assessments gave factual correctness **0.6/2** and teaching usefulness
**0.8/2** across those five samples. These are subjective AI assessments, not human
ratings or a reliability benchmark. Specific remaining problems:

- The known buggy Two Sum II draft moves both boundaries unconditionally. The model
  wrongly praised it as conditional movement. A final source-tracing prompt recheck
  also missed this defect; `LEARNING_REVIEW_TRACE_CHECK.json` retains that result
  (one structurally valid answer, 62.23 seconds, factual/usefulness ratings 0/2).
- The binary-search follow-up reversed the lower-bound comparison (`>=` became `<=`).
- Alternative comparison included an incorrect claim about halving two-pointer
  search space each step. Other responses added misleading duplicate/fixed-window
  reasoning despite useful core observations.

Authored lesson definitions are correct on these points and remain the more reliable
learning reference. Broader teacher review and fixed-mistake evaluations are needed
before promoting AI review as dependable. Prompt adjustments alone did not resolve
the known source-analysis failure; no unsupported reliability claim is made.

## Safety and persistence limits

The API remains localhost-only. There is no execution endpoint, browser-controlled
trusted flag, generic Ollama proxy, arbitrary file access, or model-code compilation.
Run stays disabled; the host C++ runner is for explicitly trusted local code and
resource safeguards are not a sandbox. Reviews use source strictly as model input.

Drafts remain browser-origin storage. Review/follow-up responses are ephemeral;
SQLite attempt/session summaries and scheduled revision remain unfinished. Existing
database/repository code is reused without replacing or reseeding the actual database.
Validated token streaming remains unavailable. No paid infrastructure, RAG, agent
framework, recommendation algorithm, or new runtime dependency was added.

## Launch and next step

Launch commands are unchanged (see `FRONTEND.md`):

```powershell
# Repository root, first terminal
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
# Second terminal
cd frontend
npm.cmd run dev
```

Open http://127.0.0.1:5173. Local Ollama with `qwen3.5:4b` is required only for AI
requests. Catalogue, authored lessons, drafts, and reference/mock reports work offline.

Stop for hands-on testing. Then prioritize the demonstrated teaching-quality failures
alongside Milestone 2.2 persistence/session-summary integration. Do not enable arbitrary
execution before meaningful isolation is independently verified.

## Automated verification and regression coverage

- Final complete Python suite: **157 passed, zero skipped, 144.68 seconds**.
  Two existing Starlette/httpx/anyio test-client deprecation warnings remain.
- Final frontend Vitest suite: **26 passed**. ESLint with zero-warning policy and
  TypeScript/Vite production build passed. Existing lazy Monaco bundle-size warning
  remains visible (~696 KiB gzip); the main bundle is ~81 KiB gzip.
- Final official-source recheck: **133 matching number/title/URL/difficulty records**.
- New regression coverage: official mappings/uniqueness/duplicate rejection, exact
  53-record preservation, reseeding from the old catalogue with unchanged attempts,
  test evidence, hints, diagnoses, and pre-submission sessions; future source identity;
  lesson-topic coverage/links/diagram bounds; CLI official labels; review consent,
  alternatives, verdict/code rejection, mode/lesson identity, malformed/truncated/
  timeout recovery, bounded attempts, and retained strict lesson response bounds.
- Frontend checks cover all search fields and three deterministic sort modes,
  official labels, lesson walkthrough/practice navigation with draft restoration,
  default independent/hint-only modes, optional-review consent, failure/retry,
  comparison tradeoffs, edited-snapshot labeling, and catalogue-only restrictions.
- Existing count assertions changed from 53 to 133 for the authorized expansion;
  stronger exact original-record and history-preservation checks were added. No
  failure-case assertion was removed to obtain a passing result.
- Running API and Vite proxy each returned 133 questions; API returned 16 lessons,
  10 verified fixtures, and built frontend HTTP 200. No actual learner DB was seeded.

The sandboxed API test attempt stalled and was stopped; the reported successful
runs used approved localhost access. This is separate from model response failures.

## Manual browser verification

Used the computer-use skill with the real local app and actual Monaco editor:

- Official `#167 — title` search opened the correct question and preserved the prior
  draft comment. Review stayed disabled until its explicit consent checkbox.
- Binary-search walkthrough controls advanced reviewed states; its #704 practice
  link opened Independent Practice. Related-question links displayed official numbers.
- Tree diagram states and officially numbered related links were checked.
- 390px mobile layout showed no horizontal overflow; desktop learning layout was
  inspected. Temporary viewport overrides were reset before handoff.
- A real tree-lesson follow-up passed through the restarted API to local Qwen and
  displayed labeled feedback. The first stale-token request showed a recoverable
  error; Retry refreshed authorization and succeeded. Core leaf-height explanation
  was correct (1), but its uncertainty text incorrectly suggested the supplied null
  base case was unspecified. This is another mixed-quality example, not a proof of
  general correctness.
- Captured browser console had no errors/warnings. Both servers and the practice
  tab remain available. Screenshot: learning-expansion.jpg.

No further milestone was implemented after this verification.
