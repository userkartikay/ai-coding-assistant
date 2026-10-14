# Independent-audit remediation verification

Date: 2026-10-12. Architecture retained: direct Ollama, Pydantic, plain SQLite,
deterministic C++ judge, and the existing CLI. FastAPI and frontend phases remain
planned. No paid dependency, RAG, agent framework, or additional milestone was added.

## Data and curriculum corrections

- backend/db/repository.py uses update-preserving upserts, savepoint rollback,
  deterministic attempt ordering, solved-flag preservation, and session associations.
- backend/db/schema.py adds practice_sessions/session_hints/aliases without replacing
  legacy learning tables. scripts/seed_db.py consolidates old slugs atomically after
  remapping dependencies, archives original duplicate metadata, and retains IDs/code/
  test results/hints/diagnoses. Reseeding is history-preserving.
- backend/curriculum/identity.py and registry.py join 53 curated entries to 10
  executable fixtures using stable LeetCode identifiers. The 43 other entries remain
  catalogue-only. Original curated provenance and difficulty are retained.
- The actual user database was not modified. Migrations were tested on temporary v1
  databases and in-memory connections, including repeated seeds and failure rollback.

## Judging and execution corrections

- Empty suites raise a configuration error before compilation. AC means only that
  the submitted program passed the available verified suite.
- All ten fixtures now include boundary and documented maximum-input cases with
  analytically expected answers. Required signatures are explicit rather than
  inferred from the first helper function.
- The old Islands recursion fails with Windows exception 0xC00000FD (stack overflow)
  on the 300x300 all-land case. Suppressing fault dialogs exposes the fault instead
  of a misleading timeout. Iterative traversal passes that same case at two seconds.
  Iterative depth-first tree traversal also handles the 10,000-node skew case while
  preserving the O(H) auxiliary-space target.
- backend/runner/process.py reads pipes concurrently into byte-capped buffers and
  terminates on overflow; compiler output and stderr are bounded too. Explicit
  OUTPUT_LIMIT and MEMORY_LIMIT verdicts avoid describing resource failure as WA.
- Timeout/overflow/memory cleanup kills and waits for observed descendants. Input is
  written concurrently so large valid test input cannot deadlock blocked pipes.
- Compilation and execution require trusted=True. CLI execution is disabled by
  default; python scripts/demo_cli.py --trusted-local acknowledges code the user
  authored or independently reviewed. This flag is an acknowledgement, not a sandbox.

## Tutor and measurement corrections

- Sequential backend hint gating advances only after successful validation and any
  optional hint write. Failed L1 generation gives a fixed neutral nudge and leaves
  state unchanged; failed L2-L5 generation is explicit.
- Pydantic validates nonempty content, questions in L1-L3, no obvious executable code
  below L5, language-agnostic L4 pseudocode, and L5 code/explanation/complexity fields.
  Responses must match the requested tier. The reproduced L2 conditional-pointer
  update disclosure is rejected and its prompt no longer requests update rules.
- Native Ollama JSON schemas, tier-specific budgets, complete-response checks, and at
  most two sequential attempts repair the tested L4/L5 malformed generation path.
  Empty response/thinking-only answers and length-terminated completions are rejected.
- Conservative byte budgeting reserves response and request/retry overhead. Context
  is 4096 tokens normally, 8192 at most, or the request is refused. This can reject
  long submissions; no hidden summarization has been introduced.
- A small Tutor protocol provides an adapter boundary without orchestration.
- Streaming metrics now ignore thinking chunks, use native eval_count token totals,
  and separate first raw JSON bytes from validated hint completion. The benchmark
  scripts save new measured JSON instead of regenerating unsupported success prose.
  New benchmark implementations were regression-tested offline, not rebenchmarked
  end-to-end during this task.

## Regression evidence and tests

Eleven new tests in test_audit_regressions.py failed before implementation, then all
passed. They cover destructive upserts, timestamp ties, duplicated seed identities,
invalid hint payloads, failed unlock leakage/state, tier skipping, early pattern
revelation, helper signatures, and mismatched response levels.

Other audit baseline evidence is recorded in PROGRESS.md. Additional regression suites:

- test_persistence_remediation.py: populated reseeding, additive v1 migration,
  archived metadata, pre-submission hints, session/problem consistency, failed child
  insert rollback, atomic seed rollback, and registry joins.
- test_execution_remediation.py: empty suite, explicit trust restriction, infinite
  stdout/stderr bounds, compiler diagnostics, child timeout cleanup, sampled memory,
  the n=1 false-AC reproduction, maximum Islands input, and limited AC wording.
- test_tutor_remediation.py: all five tier requirements, code/pattern leakage,
  malformed/truncated/empty/wrong-level/timeout recovery, exactly two attempts,
  oversized context rejection, sequential unlocks, and session hint logging.
- test_evaluation_remediation.py: all five tiers are evaluated, category mismatches
  remain visible, quality scores are absent without review, and reviews require exact
  output hashes and evidence.
- test_benchmark_remediation.py: thinking is not counted as hint latency or token
  totals; truncated streaming JSON is not a validated hint.

Existing tests were strengthened rather than weakened: newest-first now checks order,
seed count must equal 53, live diagnosis uses actual runner evidence, CLI statements
must not expose patterns, and flooding expects an explicit resource-limit verdict.
Trusted fixture calls now acknowledge trust explicitly. Original verdict and
canonical/buggy tests remain in the complete suite.

## Automated suite results

- Audit baseline: 62 passed, 0 skipped, 238.50 s.
- Focused corrected data/tutor checks: 32 passed, 4.14 s.
- Persistence/execution/expanded-fixture checks: 43 passed, 51.57 s.
- Tutor boundary/recovery checks: 29 passed, 1.69 s.
- Offline evaluator/CLI checks: 7 passed, 2 live tests deselected, 8.96 s.
- First integrated run: 110 passed, 0 skipped, 223.34 s.
- Refined offline checks: 38 passed, 4.01 s; benchmark/tier checks: 21 passed, 1.25 s.
- Final integrated run: **113 passed, zero skipped, 138.20 seconds** after all corrections.

Command: python -B -m pytest -p no:cacheprovider -q with
PYTHONDONTWRITEBYTECODE=1. Host access was required for localhost Ollama and MinGW;
project bytecode/cache writes were disabled. Temporary test databases/executables
were used. No existing learner data was deleted or migrated during the task.

## Live model evaluation, separate from automated verification

REMEDIATION_EVALUATION.json records one Two Sum II mistake and all five hint tiers.
All five returned structurally valid matching tiers; the diagnosis category matched.
L4 and L5 were rechecked with final generation handling (42.82 s and 44.32 s for this
sample). L2 was rerun after the review-discovered over-disclosure (13.96 s). L1/L3
were recorded during the initial remediation evaluation. The earlier L2 output is
retained in INITIAL_REMEDIATION_EVALUATION.json; the correction is not hidden.

Six exact-hash-linked ratings in REVIEWER_RATINGS.json are subjective Codex AI
inspection, not human assessment. Scale: 0 incorrect/unhelpful; 1 partial or minor
issues; 2 correct/useful for this inspected sample. Mean factual correctness is
1.33/2 and teaching usefulness 1.50/2. Those values describe six outputs for ONE
problem and must not be generalized to the curriculum.

Remaining observed issues include ambiguous L1 questioning, L3 termination wording
that can suggest allowing equal indices, a diagnosis focus naming an absent else-if
branch, and L5 explaining a decision rule rather than the actual search invariant.
Generated L5 code was inspected as text but not executed or marked judged. Category
matching, schema compliance, and regex leakage counts are not correctness proof.

The evaluator supports all ten fixed mistakes and all five tiers sequentially; that
full 50-hint live matrix was not run here. Automated fake-provider checks verify its
coverage logic. Human teaching-quality ratings and learning-outcome studies remain
unperformed. The historical zero-leakage/10-of-10-accuracy claims are withdrawn.

## Remaining safety limits and handoff

Sampled RSS limits (256 MiB execution, 512 MiB compiler, 20 ms interval) are soft and
can miss transient peaks. Process tracking can miss escaping descendants. Windows
Job Objects would improve kernel limits but would not isolate filesystem/network
access. Temporary cleanup remains best-effort. Host execution has full privileges.
No arbitrary execution HTTP endpoint may be introduced before Milestone 5.1 isolation
is implemented and verified. Meaningful untrusted-code isolation remains a blocker.

Milestone 2.2 may resume only as trusted-local persistence work after review of this
report. Complete CLI attempt/diagnosis logging and summaries remain unfinished; the
optional session/hint association is remediation groundwork. Keep phase ordering and
stop here before implementing those features or any frontend work.
