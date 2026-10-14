# Frontend MVP plan

The user explicitly prioritizes this MVP ahead of completing Milestone 2.2.
The existing phase numbers remain; the frontend and minimal API work are an
authorized sequencing exception, not a completion claim for persistence.

1. Add a small FastAPI adapter: registry browsing, bounded in-memory hint sessions,
   existing backend tier validation, localhost origin protections, and read-only
   trusted-reference reports. No browser code execution route or direct Ollama access.
2. Export deterministic reports from the repository's explicitly trusted canonical
   and known-bug fixtures through a manual local script. Label these as reference
   examples; the student's draft is never evaluated. Offer a separately labeled mock
   compiler/result preview for UI exploration.
3. Build React + TypeScript + Vite and locally bundled Monaco. Provide catalogue
   search/filters, independent/guided practice, per-question drafts, responsive
   resizable panels, themes, progressive mentor interaction, and result inspection.
4. Test API safety, hint failure/state semantics, catalogue fidelity, draft restoration,
   filters, modes, and mock/reference labels. Run type/build/lint checks and browser
   verification. Keep local services running for hands-on testing.
5. Record observed checks, launch commands, remaining restrictions, and the authorized
   sequence change in PLAN.md, PROGRESS.md, and DECISIONS.md. Stop for user testing.

Constraints: no SQLite rewrite, analytics, recommendations, RAG, orchestration,
voice, publishing, or untrusted execution. Catalogue-only entries show missing
statements/constraints explicitly; no content is invented. Model latency is visible
as elapsed waiting time, not fake streamed output or a promised percentage.
