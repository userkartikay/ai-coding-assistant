# Architectural Decisions & Technical Rationale

This document records architectural evaluations, empirical findings, and decisions made for the local-first AI DSA Coding Mentor.

---

## Decision 1: Direct Ollama REST Client over Heavy Frameworks (Deferred Multi-Agent/RAG)

- **Context**: The project uses `qwen3.5:4b` running locally via Ollama on an NVIDIA RTX 2050 and 16 GB system RAM.
- **Empirical Hardware Finding**:
  - `ollama ps` confirms the model is loaded with a **50% CPU / 50% GPU** distribution (2455 MiB dedicated VRAM out of 4096 MiB total; remaining layers reside in system RAM).
  - Cross-bus PCIe transfer results in an empirical generation speed of **~7.0 to 8.4 tokens/second**.
  - Multi-agent sequential turn loops (3–5 sequential LLM calls) would produce unacceptably high user latency (40–90 seconds per hint request).
- **Decision**: Use a direct, asynchronous HTTP client communicating with Ollama's native API. Single-turn, schema-constrained prompts keep latency predictable (~15–20s for short hints).
- **Policy on Multi-Agent & RAG**: Deferred, not rejected. They will be revisited only if concrete pedagogical evaluations demonstrate a value that justifies the latency multiplication.

---

## Decision 2: Extensible, Structured Question Catalogue & Evaluation Dataset

- **Context**: DSA placement preparation requires reliable, high-yield canonical problems, but must also accommodate growth and user-provided problems.
- **Decision**:
  - Standardized relational/JSON schema for problems, canonical solutions, driver harnesses, and test suites.
  - Initial curated core of canonical problems categorized by pattern and subpattern.
  - Established a version-controlled evaluation dataset (`backend/eval/dataset.py`) containing verified canonical problems and representative student flaws (e.g. boundary off-by-one, state transition bugs, unhandled negative array invariants).
  - Evaluation harness (`backend/eval/evaluator.py`) verifies that canonical solutions pass 100%, buggy submissions fail deterministically, and records tutor outputs for separate structural and human review; zero leakage is not established.

---

## Decision 3: Code Execution Safety & Environment Isolation Policy

- **Context**: Evaluating student C++ code against test suites.
- **Strict Clarification on Terminology**: Host subprocess execution, temporary working directories, and process timeouts are **runtime process safeguards for trusted local test code**, NOT a secure execution sandbox. They protect against runaway loops and output flooding during local development, but provide no isolation against untrusted or malicious host interaction.
- **Decision**:
  - During Phase 1, `CppRunner` only executes explicitly trusted local test code authored for verification.
  - All test runner functionality remains an internal Python library, completely inaccessible from external network requests.
  - Before untrusted student code execution is supported, design, implement, and verify a properly isolated execution environment.
  - Cleanup is best-effort via `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` and explicit process tree termination (`_kill_process_tree`) with process exit waiting.

---

## Decision 4: Deterministic Judge as Ground Truth (Never Trust LLM for Correctness)

- **Context**: Evaluating correctness of student code.
- **Decision**: The test runner is the sole authoritative judge of correctness.
  - `g++ -std=c++14 -O2` determines syntactic and type correctness.
  - Test suites produce deterministic verdicts: `AC`, `WA`, `TLE`, `COMPILATION_ERROR`, and `RUNTIME_ERROR`.
  - The LLM tutor is only invoked to provide educational guidance (Socratic questions, progressive hints, pattern nudges, and conceptual diagnosis of verified failures).
- **Consequences**: Verdicts are deterministic for the available tests. Passing those tests is not a proof for all inputs, complexity targets, or teaching accuracy.

---

## Decision 5: Five-Tier Socratic Guidance & Anti-Leakage Model

- **Context**: Providing progressive assistance without spoon-feeding answers.
- **Decision**:
  - Gated hierarchy (enforced in backend logic after remediation): Level 1 (Nudge) $\rightarrow$ Level 2 (Pattern) $\rightarrow$ Level 3 (Algorithm) $\rightarrow$ Level 4 (Pseudocode) $\rightarrow$ Level 5 (Solution).
  - Mistake diagnosis identifies the underlying misconception from compiler diagnostics or failing test I/O diffs, formulating a targeted Socratic question rather than rewriting code.
  - The historical evaluation inspected only Level 1 and two response fields with a limited regex. It cannot substantiate zero leakage across Levels 1–3. All tiers now have separate structural and human-quality evaluation.

---

## Decision 6: Streaming UI Requirement (Time to First Token Optimization)

- **Context**: Qwen 3.5 4B generation speed on the 50/50 CPU/GPU distribution is ~7.0–8.4 tokens/second.
- **Empirical Measurement**:
  - Batched completion takes 15–30 seconds for complete JSON blocks.
  - Time to First Token (TTFT) via streaming is **1964 ms (~1.9 seconds)**.
- **Correction after audit**: The old benchmark counted thinking chunks as first tokens. No two-second usable-answer guarantee is established. Future UI streaming must distinguish activity, validated guidance, and internal reasoning; model reasoning is never displayed as the final answer.

---

## Decision 7: Manual Repository Inspection over Automated GitHub Importers

- **Context**: User provided their existing LeetCode solutions repository (`https://github.com/userkartikay/leetcode-solutions`).
- **Decision**: Reject building an automated GitHub scraper, crawler, or repo-sync background daemon.
  - Manual inspection revealed high concentrations of Two Pointers, Sliding Window, and Monotonic Stack problems, alongside SQL/database queries and repetitive prefix sum variants.
  - More importantly, manual review caught critical syllabus voids: **Graphs (0%)**, **2D Dynamic Programming (0%)**, **Intervals (0%)**, and advanced BST reasoning (0%).
  - An automated scraper would have ingested redundancies and failed to detect syllabus gaps. A curated master curriculum of 50 problems bridges these placement gaps while preserving historical solutions as reference examples.

---

## Decision 8: Interactive Terminal Prototype as Validation Gate

- **Context**: Milestone 1.3 requires demonstrating end-to-end learning before frontend development.
- **Decision**: Implemented `SocraticCliApp` (`backend/cli/interactive_cli.py` & `scripts/demo_cli.py`) validating:
  - Problem selection and signature display.
  - Local C++ compilation via `g++` and deterministic grading (AC, WA, TLE, RTE, Compile Error).
  - Failing test case evidence handoff to Qwen 3.5 4B.
  - Progressive 5-tier hints and Socratic guiding questions.
  - Immediate in-memory revision and resubmission.
- **Consequences**: Validated the entire learning feedback loop without premature web or frontend dependencies.


## Decision 9: Plain SQLite with history-preserving writes

Retain sqlite3, WAL, and foreign keys. Use ON CONFLICT DO UPDATE instead of row
replacement. Repository writes use savepoints so failed child inserts roll back
without committing an incomplete attempt or an enclosing caller transaction.
Order attempt timestamps with ID DESC as a deterministic tie-breaker.

## Decision 10: Stable curriculum identities and additive migration

Use lc_<LeetCode number> for both curated metadata and executable fixtures. A small
registry joins them and distinguishes 43 catalogue-only entries from 10 executable
entries. Preserve curated difficulty, provenance, prerequisites, and complexity
metadata. Legacy slugs resolve through problem_aliases; their original metadata is
archived before duplicate rows are consolidated. Attempt IDs, code, test results,
hints, and diagnoses are retained. No user's real database is migrated as part of
this remediation; migration behavior is verified on temporary legacy fixtures.

## Decision 11: Practice sessions for hints before submission

Add practice_sessions and session_hints without rebuilding old history tables.
Attempts optionally reference a session; a cross-problem association is rejected.
Legacy attempt-associated hints remain readable. CLI supports an injected connection
for session/hint association; complete attempt and diagnosis integration remains 2.2.

## Decision 12: Trusted local resource safeguards, not sandboxing

Execution and compilation require explicit trusted acknowledgement. The CLI disables
submission by default and exposes --trusted-local only for source the user authored
or reviewed. Read stdout/stderr concurrently into capped byte buffers and terminate
on overflow. Bound compiler output as well. Kill and wait for observed descendants
on success, timeout, overflow, and memory excess; use temporary working directories.
Suppress Windows crash dialogs so a fault does not wait for desktop interaction.

Use 256 MiB execution and 512 MiB compiler RSS budgets with 20 ms polling across the
observed process tree. These are soft sampled limits: a fast allocation can exceed
them between samples. Windows Job Objects would supply stronger kernel limits but
also require tested job assignment/child containment and still would not isolate
files or networking. Do not claim sampled RSS or process tracking is secure isolation.
Untrusted execution remains blocked until 5.1; no execution HTTP endpoint exists.

## Decision 13: Structural hint validation and bounded model recovery

Retain direct Ollama and Pydantic. Supply a JSON schema, reject length-terminated,
empty, malformed, or wrong-tier answers, and try at most twice sequentially with
bounded completion budgets. Use 4096 tokens normally, at most 8192 when a conservative byte budget needs it; reject oversized inputs instead
of silently discarding student evidence. Separate L4 pseudocode and L5 code,
explanation, and complexity fields. Never convert internal thinking into an answer.

Enforce sequential unlocks in the backend, and advance state only after validation
and optional hint persistence succeed. Level 1 failure returns a fixed neutral nudge
and does not unlock anything; higher-tier failure is explicit. Structural validation
and heuristic leakage checks cannot guarantee the absence of semantic solution leaks.
A small Tutor protocol preserves provider independence without adding a framework.

## Decision 14: Constraint-aware reference verification and AC semantics

Reject empty suites. AC means all available verified tests passed, not proof of
universal correctness. Add analytically expected boundary and maximum-input cases.
Replace recursive islands traversal with an explicit stack: the old 90,000-cell
path stressed the default Windows stack, and faults could wait behind crash dialogs.
Use an iterative depth-first tree traversal for the 10,000-node skew case as well. Store required
function signatures explicitly; do not derive them from the first helper function.

## Decision 15: Separate structural evaluation from teaching quality

Evaluate all five tiers and fixed buggy submissions sequentially. Record schema
success/failure, category agreement, heuristic leaks, and exact output hashes. Reviewer factual correctness (0-2) and teaching usefulness (0-2) require separate
evidence and ratings tied to that exact hash. Every review identifies whether the
reviewer is human or AI; AI review must not be labeled human assessment. Unreviewed outputs have no quality score. Never run
model-generated C++ automatically: it is untrusted until independently reviewed.
Historical zero-leakage and 10/10 accuracy claims are withdrawn. Preserve their
original reports as historical artifacts with corrections rather than replacing
observations with canned success statements.


## Decision 16: User-authorized frontend-first increment

The user explicitly prioritized a frontend MVP before completing 2.2 and clarified
that the two-hour scope should stop after the usable MVP for hands-on testing. Keep
phase identifiers, document this execution-order exception, and implement only the
minimum API adapter needed by the frontend. No persistent analytics, recommendation,
RAG, multi-agent framework, voice, GitHub automation, or learner-history rewrite.

## Decision 17: Local frontend and thin FastAPI adapter

React/TypeScript/Vite serve a locally bundled Monaco C++ editor and its worker; no
CDN or external font is needed at runtime. Limit language registration to C++ and
lazy-load the editor. Monaco remains the large optional editor bundle (~696 KiB gzip)
and produces a build size warning; do not suppress the warning or load every language.
Per-question drafts use browser localStorage with explicit storage errors and file
export. Theme preferences persist; Independent Practice is the initial mode on every
page load. Guided Learning explicitly reveals catalogue teaching metadata.

API endpoints reuse the curriculum registry and SocraticCliApp tier logic. The
browser sends problem IDs and hint levels, never source code to an execution route.
Ollama is called only by the backend. Sessions are bounded (100, two-hour idle TTL),
kept in memory, and restored by opaque per-tab session IDs; they are not SQLite
attempt persistence. One API model request runs at a time to fit local hardware.
Failures return errors without treating the CLI's neutral fallback as an unlock.

Bind the API and Vite to 127.0.0.1. Use exact local origins, local Host validation,
and an ephemeral bootstrap token for session mutation/readback. This reduces
cross-origin invocation and DNS rebinding exposure but is not authentication against
other local programs, a network deployment design, or a code-execution sandbox.
No generic Ollama proxy exists. Built assets can alternatively be served by FastAPI.

## Decision 18: Browser execution disabled; reference evidence and mock preview

Keep the Run action visibly disabled. There is no endpoint accepting arbitrary C++,
no browser-controlled trusted flag, and no per-request compilation. A manual local
export script runs only repository-authored canonical/known-bug fixtures with explicit
trusted acknowledgement. Saved reports contain structured verdicts and failure I/O,
are fingerprinted against the current fixtures, and expose no reference source code.
Large report fields are labeled excerpts. API routes only read those artifacts.

Show reference results as evidence about the fixture, never the student's draft.
A separately labeled mock preview covers compiler/process error rendering without
pretending to execute anything. AC wording stays limited to the available suite.
Catalogue-only entries show missing content and disabled grounded tutoring. Do not
invent problem statements, signatures, examples, constraints, or metadata.

## Decision 19: Complete-response presentation and frontend verification

The existing tutor client has no validated token stream. Show elapsed generation
state and render only completed validated output; do not fake streaming or display
internal reasoning. Keep schema/tier checks on the backend and copy only presentation
state to React. Failed tiers remain locked, sessions recover explicitly after expiry
or server restart, and Level 5 needs a deliberate reveal acknowledgement.

Verify browser interactions alongside isolated UI and API tests. Unit tests stub
Monaco for DOM testing; manually verify the actual bundled editor, worker, coloring,
drafts, layouts, and real Qwen request separately. Existing SQLite and runner tests
remain part of the complete backend suite. Pin the available patched DOMPurify
3.4.17 override for Monaco 0.57.0's vulnerable 3.4.15 dependency; the npm production
audit then reports zero known advisories. This is not a claim of universal security.

## Decision 20: Official source identities and non-destructive expansion

The user requested 120–150 questions with official LeetCode numbering. Keep the
existing 53 objects unchanged; append 80 distinct catalogue-only records. Store
LeetCode numbers in `leetcode_id`, retain internal `lc_<number>` IDs and existing
aliases, and preserve draft keys and learning references. Compare official number,
title, slug URL, and difficulty to LeetCode's public catalogue with a read-only
verification utility and checked-in manifest. Metadata verification does not imply
verified constraints or an executable judge. Unknown constraints/signatures remain
unavailable; original concise summaries are stored separately by official number.
Future local questions have source-specific IDs and cannot invent LeetCode numbers.

## Decision 21: Optional reviewed learning material and static AI review

Add a small reusable lesson schema and 16 authored starter lessons covering the
requested families, rather than generating lessons dynamically. Reviewed walkthrough
states are navigable visual examples, not an arbitrary-code simulator. Preserve
legacy primary/subpattern metadata; group related labels at lesson level. Link to
practice using official identities and retain the student's chosen practice mode.

Hint Only uses existing tier gating. Approach review and alternative comparison are
separate opt-in teaching modes requiring explicit consent to reveal patterns and
complexities. They return static analysis, uncertainty, and guiding questions;
comparison requires distinct alternatives with tradeoffs. They never compile source,
create verdicts, advance hints, or reuse fixture results as student evidence. Only
questions with verified statement grounding currently enable review. Edited drafts
mark earlier feedback as belonging to an earlier snapshot. No new persistence layer.

Lesson questions receive selected lesson material only. All new model routes share
the existing local token/origin boundaries and one model-call lock. Use two bounded
attempts, validate requested context/mode, and give the retry validation reasons
without source-input dumps. Keep the 8K context ceiling, including repair text.

## Decision 22: Ollama grammar compatibility and quality evidence

Live Qwen/Ollama returned HTTP 400 `failed to parse grammar` for the lesson answer
schema. A diagnostic request succeeded when string length constraints were omitted
from the sampler grammar. Omit those generation-only bounds for lesson answers;
retain all original Pydantic length bounds, section enums, identity validation,
completion checks, and negative tests. Other response schemas retain their native
constraints. This compatibility adjustment does not relax accepted-response checks.

Live reviews can hallucinate faults even after passing schema checks. Preserve
initial failure/quality evidence and corrected samples separately. Subjective ratings
are Codex assessments, not human learner studies or a general reliability guarantee.
No model response becomes correctness evidence, and generated code is not executed.

## Decision 23: First-overhaul milestone and reliable local supervision

The new core-learning overhaul explicitly requests a stop after the first major
milestone. Implement O1 launch reliability and execution-readiness investigation;
do not expand catalogue/content/fixtures/drills/history yet. Preserve phase identities
while PLAN.md records the newly authorized order.

Use a small Python standard-library supervisor with a Windows `start.cmd` wrapper,
existing psutil only for owned-process cleanup, and no new runtime framework. Normal
launch/check does not install anything; explicit setup creates/prefer a local venv,
checks exact pinned packages and installed npm lock versions, and repairs only when
necessary. Call Node/Vite directly to avoid an extra persistent shell process.
Keep fixed loopback ports, readiness and proxy checks, actionable logs, optional
offline mode, recognized-service reuse, and cleanup only of owned processes. Do
not automatically start/download Ollama, switch Windows policies, or seed SQLite.

## Decision 24: Isolation candidate is separate from enabling execution

Read-only inspection confirms WSL2 distributions but no running Docker daemon, and
the existing runner is still a host subprocess runner. Microsoft documents that
ordinary WSL is not an untrusted-code sandbox; disabling interop/mounts does not
establish a security boundary. Native AppContainer/LPAC with explicit capabilities/
ACLs and Job limits is the first O2 candidate because it avoids an additional VM
alongside Qwen on 16 GB RAM. This is an engineering recommendation, not verified
isolation. Both compilation and execution must pass adversarial resource-access,
network, child-process and quota checks before connecting an API route.

If native containment requires unsafe broad privileges or cannot pass verification,
use a separately managed restricted VM as fallback instead of assuming WSL is safe.
Docker/Linux-container configuration is another candidate requiring a working
runtime and independent boundary review; paid Enhanced Container Isolation is
excluded. Overhead/startup comparisons are estimates until measured on this laptop.
See docs/EXECUTION_READINESS.md for primary sources and acceptance gates. No OS
configuration/runtime install or untrusted-code execution was performed in O1.
