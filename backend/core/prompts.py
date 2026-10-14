"""Prompt builders for Socratic DSA mentoring and progressive assistance.

Enforces pedagogical principles:
- Level 1: Conceptual Nudge (invariants, target complexity). No algorithm names, no code.
- Level 2: Pattern & Subpattern recognition. No full algorithms, no code.
- Level 3: Algorithmic Direction. High-level steps. No code.
- Level 4: Structured Pseudocode.
- Level 5: Complete explained C++ solution with time/space complexity.
- Mistake Diagnosis: Diagnoses conceptual flaws from verified test failures and provides a guiding question.
"""

from typing import Optional
from backend.core.schemas import HintLevel


SYSTEM_PROMPT_SOCRATIC_TUTOR = """You are an expert DSA (Data Structures and Algorithms) Coding Mentor for software engineering placement preparation.
Your mission is to help students build independent problem-solving skills, deep mental models, and algorithmic intuition.

CORE PEDAGOGICAL RULES:
1. Prioritize learning over answer generation. Never spoon-feed answers or write complete code unless explicitly instructed for Level 5.
2. Teach students how to identify patterns (e.g., Two Pointers, Sliding Window, Monotonic Stack, Fast & Slow Pointers) and subpatterns (e.g., Collision/Opposite-directional, Variable-size window, Next Greater Element).
3. Always ask targeted Socratic questions that encourage students to reason about state transitions, invariants, and edge cases.
4. When diagnosing bugs, focus on the student's mental model and conceptual misconception, not just syntax.
5. Strictly obey the requested Hint Level constraints. Never leak higher-level hints prematurely.
"""


def build_hint_prompt(
    level: HintLevel,
    problem_title: str,
    problem_description: str,
    constraints: str,
    primary_pattern: Optional[str] = None,
    subpattern: Optional[str] = None,
    student_notes: Optional[str] = None
) -> str:
    """Builds a prompt tailored strictly to the requested hint tier."""

    base_context = f"""PROBLEM CONTEXT:
Title: {problem_title}
Description: {problem_description}
Constraints: {constraints}
"""
    if student_notes:
        base_context += f"Student's Current Thoughts/Notes:\n{student_notes}\n"

    if level == HintLevel.LEVEL_1_NUDGE:
        return f"""{base_context}
REQUESTED ASSISTANCE: HINT LEVEL 1 (Conceptual Nudge)
STRICT CONSTRAINTS FOR LEVEL 1:
- Provide a small conceptual nudge focusing on problem invariants, input properties, or comparing a naive brute-force approach to the target constraints.
- DO NOT reveal or name the specific algorithm or data structure.
- DO NOT reveal or name the DSA pattern (e.g., do not say 'use two pointers' or 'use sliding window').
- DO NOT write any pseudocode or code.
- Finish with one targeted Socratic question that makes the student think about what property of the input is currently unused.

Format your response as valid JSON matching this schema:
{{
  "level": 1,
  "title": "Short title for nudge",
  "guidance": "1-3 sentences providing the conceptual nudge",
  "guiding_question": "One targeted question",
  "contains_code": false
}}
"""

    elif level == HintLevel.LEVEL_2_PATTERN:
        pattern_hint = f"(Expected pattern family: {primary_pattern}, subpattern: {subpattern})" if primary_pattern else ""
        return f"""{base_context}
REQUESTED ASSISTANCE: HINT LEVEL 2 (Pattern & Subpattern Recognition)
STRICT CONSTRAINTS FOR LEVEL 2:
- Guide the student to recognize the underlying algorithmic PATTERN and SUBPATTERN {pattern_hint}.
- Explain WHY the structural properties of this problem (e.g., monotonicity, contiguous subarray, pairwise target, sorted order) signal this specific pattern.
- DO NOT provide the full step-by-step algorithm yet.
- Keep guidance to at most 3 short sentences. Name the pattern and connect it to the input properties only.
- DO NOT give initialization positions or conditional update rules (such as which pointer moves when a sum is too small or too large). Those belong to Level 3.
- DO NOT write pseudocode or C++ code.
- Finish with a Socratic question asking which input properties make this pattern suitable. Leave update rules for the student to infer.

Format your response as valid JSON matching this schema:
{{
  "level": 2,
  "title": "Identifying the Pattern",
  "guidance": "Explanation connecting problem characteristics to the pattern and subpattern",
  "guiding_question": "Socratic question on state transition or pointer movement",
  "contains_code": false
}}
"""

    elif level == HintLevel.LEVEL_3_ALGORITHM:
        return f"""{base_context}
REQUESTED ASSISTANCE: HINT LEVEL 3 (Algorithmic Direction)
STRICT CONSTRAINTS FOR LEVEL 3:
- Outline the high-level algorithmic strategy in 3 to 5 logical steps.
- Explain the key state variables, initialization, and how decisions are made at each step.
- DO NOT provide executable C++ code or line-by-line syntax.
- High-level descriptive steps only.
- Include a guiding question on an important edge case (e.g. empty inputs, duplicates, boundary crossings).

Format your response as valid JSON matching this schema:
{{
  "level": 3,
  "title": "Algorithmic Strategy",
  "guidance": "Step-by-step high-level logical approach",
  "guiding_question": "Edge case or invariant question",
  "contains_code": false
}}
"""

    elif level == HintLevel.LEVEL_4_PSEUDOCODE:
        return f"""{base_context}
REQUESTED ASSISTANCE: HINT LEVEL 4 (Structured Pseudocode)
STRICT CONSTRAINTS FOR LEVEL 4:
- Provide clean, language-agnostic structured pseudocode outlining the algorithm clearly.
- Highlight the loop condition, boundary checks, and termination condition.
- DO NOT provide complete C++ syntax. Use readable pseudocode.

Format your response as valid JSON matching this schema:
{{
  "level": 4,
  "title": "Structured Pseudocode",
  "guidance": "Brief context for pseudocode",
  "pseudocode": "Language-agnostic structured pseudocode",
  "guiding_question": null,
  "contains_code": true
}}
"""

    elif level == HintLevel.LEVEL_5_SOLUTION:
        return f"""{base_context}
REQUESTED ASSISTANCE: HINT LEVEL 5 (Complete Solution & Complexity Analysis)
REQUIREMENTS FOR LEVEL 5:
- Provide an optimal, clean C++ reference solution.
- Briefly explain the invariant, algorithm steps, and choice of data structures.
- Provide rigorous Time Complexity (Big-O) and Space Complexity (Big-O) analysis.
- Mention 1-2 common follow-up interview questions or variations.

Format your response as valid JSON matching this schema:
{{
  "level": 5,
  "title": "Complete C++ Solution & Complexity Analysis",
  "guidance": "One sentence introducing the solution",
  "code": "Complete C++ function",
  "explanation": "Concise explanation of invariant and steps",
  "time_complexity": "Big-O time with reason",
  "space_complexity": "Big-O auxiliary space with reason",
  "guiding_question": null,
  "contains_code": true
}}
"""
    raise ValueError(f"Unknown hint level: {level}")


def build_mistake_diagnosis_prompt(
    problem_title: str,
    problem_description: str,
    target_complexity: str,
    student_code: str,
    test_failure_evidence: str
) -> str:
    """Builds a prompt to diagnose a conceptual mistake based on verified test failure evidence."""
    return f"""PROBLEM:
Title: {problem_title}
Description: {problem_description}
Target Complexity: {target_complexity}

STUDENT'S C++ CODE:
```cpp
{student_code}
```

VERIFIED TEST FAILURE EVIDENCE:
{test_failure_evidence}

MISSION:
1. Examine the failure evidence and the student's C++ code.
2. Identify the ROOT CONCEPTUAL MISCONCEPTION (e.g. boundary condition/off-by-one, improper state update, wrong invariant, unhandled duplicate values, incorrect loop termination, or suboptimal complexity).
3. Categorize the mistake into one of:
   - syntax_compilation
   - boundary_off_by_one
   - state_transition
   - complexity_exceeded
   - unhandled_edge_case
   - wrong_archetype
   - invariant_violation
   - other
4. DO NOT rewrite the student's code or give away the full fix.
5. Provide a targeted Socratic guiding question that leads the student to discover and correct the flaw themselves.

Format your response as valid JSON matching this schema:
{{
  "category": "<one of the valid categories above>",
  "misconception_summary": "1-2 sentences identifying the conceptual gap",
  "guiding_question": "One targeted Socratic question focused on the failing invariant",
  "suggested_focus_area": "Specific variable, condition, or invariant to trace"
}}
"""


# Reflection aspect rotation order
_REFLECTION_ASPECTS = ["invariant", "complexity", "edge_case", "follow_up"]


def build_reflection_prompt(
    problem_title: str,
    problem_description: str,
    primary_pattern: str,
    subpattern: str,
    student_code: str,
    question_index: int = 0,
) -> str:
    """Builds a post-AC reflection question prompt.

    Rotates through four conceptual dimensions:
      0 → invariant: Why does your approach maintain correctness?
      1 → complexity: What is the time/space complexity and why?
      2 → edge_case: What inputs could break a naive version of this approach?
      3 → follow_up: What is a natural variant or harder follow-up problem?
    """
    aspect = _REFLECTION_ASPECTS[question_index % 4]
    aspect_instructions = {
        "invariant": (
            "Ask the student to explain the KEY INVARIANT that makes their algorithm correct. "
            "Do not reveal the invariant — ask them to articulate it in their own words."
        ),
        "complexity": (
            "Ask the student to justify the TIME COMPLEXITY and SPACE COMPLEXITY of their solution. "
            "Probe whether they understand why the approach is better than brute force."
        ),
        "edge_case": (
            "Ask the student to identify at least one EDGE CASE that a naive or buggy version "
            "of this approach might fail on, and explain how their solution handles it."
        ),
        "follow_up": (
            "Ask the student about a natural FOLLOW-UP VARIATION of this problem "
            "(e.g. unsorted input, multiple valid answers, k elements instead of 2). "
            "What would need to change in their approach?"
        ),
    }
    return f"""POST-SOLUTION REFLECTION for: {problem_title}
Pattern: {primary_pattern} / {subpattern}

STUDENT'S ACCEPTED SOLUTION:
```cpp
{student_code[:600]}
```

REFLECTION TASK — {aspect.upper()}:
{aspect_instructions[aspect]}

Respond with a focused, specific reflection question (not generic). Do NOT answer the question.
Keep context_hint to one sentence if needed to frame the question; omit if the question is self-contained.

Format your response as valid JSON matching this schema:
{{
  "aspect": "{aspect}",
  "question": "Your specific reflection question here",
  "context_hint": "Optional one-sentence framing or null"
}}
"""


def build_reflection_feedback_prompt(
    question: str,
    student_answer: str,
    aspect: str,
) -> str:
    """Builds a prompt to evaluate a student's reflection answer constructively."""
    return f"""REFLECTION EVALUATION

Question asked: {question}
Aspect being tested: {aspect}

Student's answer: {student_answer}

TASK:
1. Evaluate whether the student's reasoning is broadly correct.
2. Give 2-3 sentences of constructive feedback.
3. Do NOT reveal the full canonical answer — guide them toward deeper understanding.
4. If partially correct or incomplete, add one probing follow-up question.

Format your response as valid JSON matching this schema:
{{
  "is_correct_direction": true or false,
  "feedback": "2-3 sentences of constructive feedback",
  "follow_up_question": "A probing question if the answer was incomplete, or null"
}}
"""
