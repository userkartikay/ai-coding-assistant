# AI Coding Mentor — Implementation Plan & Roadmap

## 1. Executive Summary & Philosophy

This plan outlines the architecture and phased roadmap for building a local-first, AI-powered DSA Coding Mentor for placement preparation.
Target environment: **NVIDIA RTX 2050 Laptop GPU (4 GB dedicated VRAM), AMD Ryzen 5 5500H, 16 GB RAM, Windows 11**, using **Qwen 3.5 4B via Ollama**.

### Core Educational Principles:
- **Pattern & Subpattern Recognition**: Train students to independently identify structural problem archetypes (e.g., Sliding Window with Variable Size, Monotonic Decreasing Stack, Opposite-Directional Two Pointers).
- **Socratic Guidance**: Ask targeted questions that prompt independent thinking rather than revealing answers.
- **Progressive Assistance**: 5 strictly gated hint tiers (Nudge $\rightarrow$ Pattern $\rightarrow$ Algorithmic Direction $\rightarrow$ Pseudocode $\rightarrow$ Explained Solution).
- **Conceptual Mistake Diagnosis**: Diagnose the mental model failure behind test errors (e.g. state management error, boundary off-by-one, temporal ordering violation) rather than just pointing out syntax.
- **Grounded Verification**: Use verified test suite and compiler execution as the sole authoritative judge of correctness, never treating LLM output as proof.

---

## 2. Hardware Budget & Empirical Benchmarks

Hardware audit confirms 4096 MiB dedicated VRAM. AGENTS.md's 6 GB target is not the dedicated capacity on this machine.
- Keep one local Qwen 3.5 4B model and sequential requests. Direct Ollama integration is retained.
- Earlier speed and offload observations in docs/BENCHMARKS.md are historical, not guaranteed current values.
- The old 1964 ms measurement included thinking chunks, not time to usable guidance.
- Production structured generation disables thinking, uses 4096 context tokens normally and at most 8192 when needed and at most two sequential attempts. Long inputs are rejected rather than silently truncated.
- Measure first user-visible guidance independently before setting a streaming latency acceptance criterion.

---

## Authorized execution-order change: frontend MVP

The user explicitly requested a usable frontend before completing Milestone 2.2,
and selected “frontend MVP first; stop for hands-on testing” within the two-hour
scope. Phase numbers are retained, but execution order is intentionally changed:
remediation -> minimum Phase 3 API adapter + Phase 4 frontend MVP -> user testing ->
Milestone 2.2 and remaining API/frontend work. This exception does not authorize
untrusted execution, analytics, RAG, orchestration, or other later-phase features.

See docs/FRONTEND_PLAN.md for the implementation increment and docs/FRONTEND.md for
launch commands, checks, and limitations. SQLite integration remains unfinished.

## 3. Revised Phased Roadmap

### Authorized core-learning overhaul sequence (2026-10-13)

The new request supersedes the earlier handoff and explicitly requires small
milestones with a stop after the first. Keep the existing architecture/phase IDs:

- **O1: Reliable local launch and execution readiness** — `start.cmd`, prerequisite
  checks/explicit dependency setup, managed localhost services, health/proxy checks,
  shutdown/reuse tests, and a source-based isolation options assessment. Stop/report.
- **O2: Execution isolation prototype and verification** — advances 5.1 before
  browser Run/Submit. First evaluate native AppContainer/LPAC plus Job Objects;
  retain disabled execution if the boundary cannot pass adversarial checks. Plain
  WSL is not a sandbox. See docs/EXECUTION_READINESS.md.
- **O3: Representative deep lesson and decision cards** — one end-to-end learning
  flow first, then reviewed content across the existing 16 families and a heuristic
  pattern-selection guide. No additional catalogue entries.
- **O4: Existing-question verification** — prioritize 40–50 high-value current
  questions, curated hints and independent oracles; quality takes precedence over
  count. No untrusted host execution; preserve all 133 identities and records.
- **O5: Recognition drills and deterministic state traces** — curated multiple
  accepted approaches, mixed practice, explain competing patterns, reusable traces.
- **O6: Persistence and revision** — complete existing 2.2 and revision groundwork
  only after execution/learning foundations, reusing SQLite with safe migrations.

O1 is the current stop point. Later steps are planned, not implemented. Launch docs:
docs/LAUNCH.md. Existing milestone definitions below remain references; this section
records the newly authorized order without claiming the entire overhaul is done.

### Phase 1: Grounded Socratic Core & Execution Engine (The Vertical Slice)
> **Goal**: Build and verify the smallest functional prototype demonstrating Socratic tutoring, progressive hints, and trusted test execution.

- **Milestone 1.1: Direct Ollama Tutor Client & Benchmarking** *(Implemented; see PROGRESS.md for current verification and limits)*
  - Direct async client to Ollama `/api/generate` with JSON-schema-constrained answers, truncation detection, and bounded recovery. Thinking is never used as the final answer.
  - Socratic prompts plus backend tier gating and structural checks. Educational correctness requires separate evaluation.
  - Pydantic schemas validating structured responses.
  - Regression tests cover schema/tier validation, malformed/truncated outputs, bounded recovery, and failed-unlock state.
- **Milestone 1.2: Trusted C++ Test Execution & Deterministic Judge** *(Implemented; see PROGRESS.md for current verification and limits)*
  - `CppRunner` compiles trusted C++ source using `g++ -std=c++14 -O2`.
  - Process safeguards: 5s compile/2s per-test limits, 10 KiB per output stream during execution, bounded compiler diagnostics, process-tree cleanup, and sampled RSS limits (256 MiB execution/512 MiB compiler). Trusted local code only; these are not isolation.
  - Deterministic judge producing structured verdicts: `AC`, `WA`, `TLE`, `COMPILATION_ERROR`, and `RUNTIME_ERROR`, `OUTPUT_LIMIT`, and `MEMORY_LIMIT`. AC means the available verified test suite passed, not universal correctness.
  - Failing evidence capture formatted for the Socratic tutor.
  - Temporary working directories and best-effort cleanup after terminating observed process trees. No guarantee against escaping descendants or Windows file locks.
  - Regression checks include verdicts, empty suites, live pipe limits, sampled memory, child cleanup, and maximum-input canonical cases.
  - Ten stable-ID executable fixtures with explicit signatures, canonical and buggy code, and boundary/maximum-input cases.
  - Evaluation covers all five tiers and every diagnosis field. Structural checks, expected category agreement, and human quality ratings are reported separately.
  - Historical test totals and quality claims are superseded by PROGRESS.md and docs/REMEDIATION.md.
- **Milestone 1.3: Vertical Slice CLI Demo** *(Implemented; see PROGRESS.md for current verification and limits)*
  - `backend/cli/interactive_cli.py`: `SocraticCliApp` connecting dataset, runner, and Ollama tutor.
  - `scripts/demo_cli.py`: Runnable interactive terminal demo.
  - Full loop: problem selection → C++ submission → deterministic verdict → Socratic diagnosis → unlockable Level 1–5 hints → revision/resubmit.
  - Graceful handling of model timeouts and malformed responses.
  - `backend/eval/dataset.py` expanded from 5 → **10 verified problems** with full driver harnesses and representative buggy submissions.
  - `backend/curriculum/catalogue.py`: **133-problem placement curriculum** (original 53 plus 80 additions), grouped into 16 starter lesson families (Two Pointers, Sliding Window, Binary Search, Graphs, Trees, DP, Stacks/Queues, Intervals, Strings, Bits, etc.).
  - `docs/CURRICULUM.md`: Repository review, redundancy analysis, and master curriculum table.
  - Current automated checks and live evaluation scope are recorded in PROGRESS.md.

---

### Phase 2: Extensible Curriculum & Attempt Persistence
> **Goal**: Establish the extensible question catalogue (15–20 canonical patterns) and local persistence for student attempts.

- **Milestone 2.1: Extensible Question Catalogue**
  - Standardized schema for DSA problems (ID, Title, Difficulty, Pattern, Subpattern, Constraints, Complexity Target, Reference Code, Driver Harness, Test Cases).
  - 133 curated entries; 10 are fully executable fixtures and 123 remain catalogue-only. Stable LeetCode IDs preserve curated provenance and metadata.
  - Ingestion utility to import personal LeetCode solutions and custom test cases.
- **Milestone 2.2: SQLite Attempt & Mistake Persistence**
  - Database groundwork implemented: update-preserving upserts, legacy-ID migration with archived metadata, deterministic ordering, savepoint rollback, and pre-submission practice sessions.
  - Deferred by the authorized frontend-first sequence. Next persistence work after hands-on frontend review: complete attempt/diagnosis persistence and session summary. The remediation adds optional session/hint association only; it does not implement the remaining milestone.
- **Milestone 2.3: Conceptual Mistake Taxonomy Engine**
  - Heuristics + AI diagnosis mapping failures to mistake categories.

---

### Phase 3: FastAPI Backend & Interactive Tutoring API
> **Goal**: Expose a clean local REST & streaming API connecting the execution runner, question catalog, and AI tutor.

- **Milestone 3.1: REST Endpoints** *(minimum frontend adapter implemented)*
  - MVP adapter: catalogue/detail endpoints, bounded ephemeral mentor sessions, health, progressive hints, fingerprinted reference reports, and explicitly labeled mock previews. Persistent attempt logging is pending. No HTTP endpoint may execute arbitrary submitted code. Execution remains a trusted local library until Milestone 5.1 isolation is verified.
- **Milestone 3.2: Streaming Socratic Dialogue (SSE)**
  - Server-Sent Events streaming with measured time to user-visible guidance. Buffer/validate structured content before presenting it as a valid hint; never show thinking as an answer.
- **Milestone 3.3: Automated Test Suite & Prompt Regression**
  - Comprehensive Pytest coverage.

---

### Phase 4: Student Frontend (React + TypeScript + Monaco Editor)
> **Goal**: Provide a focused IDE tailored for Socratic DSA learning.

- **Milestone 4.1: 3-Pane Interface** *(frontend MVP implemented)*
  - Searchable 133-question browser with official LeetCode labels and number/difficulty/topic sorting, responsive problem/editor workspace, local C++ Monaco with starter signatures and per-question drafts, mentor panel, and reference/mock test-result inspection. Missing statements and unavailable execution remain explicit.
- **Milestone 4.2: Progressive Hint Drawer with Friction** *(frontend MVP implemented)*
  - Backend-enforced sequential tiers, failed-generation retry without unlock, visible waiting time, and explicit consent before complete-solution requests. Independent practice hides pattern/subpattern/complexity metadata; guided mode reveals it.
- **Milestone 4.3: Real-Time Socratic Interaction** *(partial: validated hint interaction)*
  - All five existing hint tiers are available for executable questions. Optional static approach review, alternative comparison, and grounded lesson follow-ups are implemented for this authorized increment. Raw token streaming and unrestricted chat remain pending; the existing validated client is batched and browser code is never executed.

---

### Phase 5: Spaced Revision, Isolated Execution & Placement Readiness
> **Goal**: Verified isolation before arbitrary submissions, weakness tracking, and spaced revision. Until 5.1 passes, student execution remains disabled regardless of earlier API/frontend phases.

- **Milestone 5.1: Isolated Execution Environment**
  - Design, implement, and verify a properly isolated execution environment for untrusted code before exposing execution beyond local trusted tests.
- **Milestone 5.2: Weakness Analytics & Spaced Revision Queue**
  - Spaced revision queue (auto-scheduling problems failed or heavily hinted after 3 and 7 days).
- **Milestone 5.3: Empirical Evaluation of Deferred Concepts (RAG / Multi-Agent)**
  - Rigorous evaluation of multi-agent and RAG trade-offs against baseline.

## Historical remediation gate (completed; sequencing exception above supersedes it)

The remediation originally kept the phase sequence unchanged. It resolved the independent audit's data-loss, judging,
hint reliability, trusted-execution boundary, and identity defects; run regression and
full suites and report live model-quality limitations separately. The separate authorized frontend increment now follows that completed remediation; no taxonomy engine or importer is included.

## Authorized curriculum and learning increment (2026-10-13)

The user requested 120–150 curated questions, Learn DSA, optional solution review,
and official LeetCode numbering before resuming deferred milestones. See
`docs/EXPANSION_PLAN.md` and `docs/CURRICULUM_EXPANSION.md`.

- Milestone 2.1 catalogue expansion: 133 official identities, original 53 metadata
  records unchanged, 80 new catalogue-only entries with original summaries.
- Milestone 3.1 adapter extension: protected static review and lesson questions via
  the existing bounded Ollama client; shared single-model request lock; no execution.
- Milestone 4.4 learning experience: 16 starter lessons, 50 subpattern distinctions,
  interactive reviewed walkthrough states, linked practice, opt-in approach review
  and alternative comparison. Independent Practice remains the initial mode.
- Existing `leetcode_id` and `lc_<number>` keys remain canonical; no draft-key or
  learner-history migration is needed. Identity verification is separate from
  fixture verification. Future non-LeetCode sources use source-specific identities.
- Stop for hands-on testing after this increment. Milestone 2.2 SQLite integration,
  session summaries, isolated execution, and later phases remain unfinished.
