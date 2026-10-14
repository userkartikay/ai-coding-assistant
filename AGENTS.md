# Agents Overview

# AI Coding Mentor — Agent Instructions

## 1. Project Mission

Build a local-first AI-powered DSA teaching application for students preparing for software engineering placements.

The system must help students develop independent problem-solving abilities, not merely generate solutions.

Primary model: Qwen 3.5 4B through Ollama.
Model integration must remain provider-independent.

## 2. Development Environment

Target hardware:
- NVIDIA RTX 2050 Laptop GPU, 6 GB VRAM
- AMD Ryzen 5 5500H
- 16 GB system RAM
- Windows development environment

The application must remain practical on this hardware.

Avoid unnecessary cloud dependencies, large concurrent models, and memory-intensive infrastructure.

Preferred initial stack:
- React + TypeScript
- Monaco Editor
- FastAPI
- SQLite
- Ollama
- Pytest

These are preferences, not immutable requirements.

## 3. Core Learning Principles

The application must:

1. Help students recognize DSA patterns and subpatterns.
2. Use Socratic questioning rather than immediately revealing solutions.
3. Support progressive hints.
4. Analyze incorrect C++ code.
5. Explain conceptual mistakes, not just syntax errors.
6. Track attempts, mistakes, and improvements.
7. Support revision based on previous weaknesses.
8. Use verified test results when determining correctness.

The tutor must prioritize learning over answer generation.

Do not treat LLM output as authoritative proof of correctness.

## 4. Agent Autonomy

You are an engineering partner, not a blind executor.

You MAY:
- Challenge the existing implementation plan.
- Reorder development phases.
- Replace libraries or frameworks.
- Simplify overengineered designs.
- Remove unnecessary implementation steps.
- Add useful tests or safeguards.
- Recommend better architectural approaches.
- Change implementation details without asking permission.

You MUST:
- Explain significant deviations from PLAN.md.
- Document architectural decisions in DECISIONS.md.
- Keep PLAN.md synchronized with accepted changes.
- Prefer small, testable implementations.
- Preserve the project's teaching mission.
- Respect hardware and cost constraints.

## 5. When Approval Is Required

Request approval before:
- Removing a core learning capability.
- Significantly changing the product's purpose.
- Introducing paid APIs or infrastructure.
- Performing destructive database changes.
- Deleting important user data.
- Introducing major external dependencies that create recurring costs.

For normal engineering decisions, proceed independently.

If the plan is unrealistic, propose and implement a feasible alternative where no approval is required.

## 6. Engineering Standards

- Prefer simple, maintainable architecture.
- Avoid premature microservices.
- Avoid multi-agent frameworks unless demonstrably useful.
- Keep business logic separate from model prompts.
- Validate model-generated structured responses.
- Never execute untrusted student code directly inside the API server.
- Use a properly isolated execution environment for submitted code.
- Protect secrets and local files.
- Write tests for important behavior.
- Do not claim tests pass unless actually executed.

## 7. Learning System Architecture

Initially prefer:
- Deterministic question selection.
- Verified question catalogue.
- Structured attempt history.
- One configurable AI tutor.
- Prompt-based teaching modes.
- Lightweight local persistence.

Add RAG, orchestration frameworks, embeddings, and advanced personalization only when there is a concrete demonstrated need.

## 8. AI Teaching Requirements

Implement progressive assistance:

Level 1: Small conceptual nudge.
Level 2: Help recognize the pattern.
Level 3: Explain the algorithmic direction.
Level 4: Provide pseudocode.
Level 5: Provide a complete explained solution.

Lower hint levels must not intentionally reveal full solutions.

For debugging:
- Read the question and student code.
- Use verified failure evidence when available.
- Identify likely misconceptions.
- Ask a targeted guiding question.
- Avoid unnecessarily rewriting the student's code.

Evaluate the tutor against a fixed set of known DSA mistakes.

## 9. Development Workflow

Before implementing a phase:
1. Read AGENTS.md, PLAN.md, and PROGRESS.md.
2. Examine the existing codebase.
3. Identify dependencies and unfinished work.
4. Evaluate whether the proposed implementation is realistic.
5. Improve the plan if justified.
6. Implement a small, testable increment.
7. Run relevant checks.
8. Update PROGRESS.md.
9. Record important decisions.

Do not rewrite unrelated working code.

## 10. Agent Handoff

Multiple coding agents may work on this repository sequentially.

Maintain PROGRESS.md with:
- Current phase
- Completed features
- Incomplete features
- Known bugs
- Tests executed and results
- Important architectural decisions
- Immediate next task

Never assume previous claims are correct without verifying relevant files and tests.

## 11. Definition of Done

A feature is complete only when:
- Its acceptance criteria are satisfied.
- Relevant automated tests pass.
- Important failure cases are considered.
- Documentation is updated.
- Its behavior has been verified, not merely implemented.

## 12. Final Priority

Prioritize:
1. Correctness
2. Teaching effectiveness
3. Reliability and security
4. Simplicity
5. Performance
6. Visual polish
7. Optional advanced features

Build a useful coding mentor, not an impressive but unreliable AI demonstration.
