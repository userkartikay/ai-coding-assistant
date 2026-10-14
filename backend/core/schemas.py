"""Pydantic schemas for Socratic DSA tutoring, hints, and mistake diagnostics."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, model_validator
import re


class HintLevel(int, Enum):
    LEVEL_1_NUDGE = 1
    LEVEL_2_PATTERN = 2
    LEVEL_3_ALGORITHM = 3
    LEVEL_4_PSEUDOCODE = 4
    LEVEL_5_SOLUTION = 5


class MistakeCategory(str, Enum):
    SYNTAX_COMPILATION = "syntax_compilation"
    BOUNDARY_OFF_BY_ONE = "boundary_off_by_one"
    STATE_TRANSITION = "state_transition"
    COMPLEXITY_EXCEEDED = "complexity_exceeded"
    UNHANDLED_EDGE_CASE = "unhandled_edge_case"
    WRONG_ARCHETYPE = "wrong_archetype"
    INVARIANT_VIOLATION = "invariant_violation"
    OTHER = "other"


class ProgressiveHintResponse(BaseModel):
    """Structured response for progressive hints."""
    level: HintLevel
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=160)
    guidance: str = Field(min_length=1, max_length=8000)
    code: Optional[str] = None
    pseudocode: Optional[str] = None
    explanation: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    guiding_question: Optional[str] = Field(
        default=None,
        description="A targeted Socratic question prompting the student to think, used in levels 1-3."
    )
    contains_code: bool = Field(
        default=False,
        strict=True,
        description="True if the response intentionally contains C++ code or pseudocode (allowed only for levels 4 and 5)."
    )

    @model_validator(mode='after')
    def validate_tier(self):
        """Structural and obvious leakage checks, not a proof of teaching quality."""
        if self.level.value <= 3:
            if self.contains_code or any((self.code, self.pseudocode, self.explanation,
                                          self.time_complexity, self.space_complexity)):
                raise ValueError('Code and pseudocode are forbidden at levels 1-3')
            if not self.guiding_question or len(self.guiding_question.strip()) < 5:
                raise ValueError('Levels 1-3 require a guiding question')
            visible = ' '.join(filter(None, (self.title, self.guidance, self.guiding_question, self.explanation)))
            if has_code(visible):
                raise ValueError('Executable code detected below level 4')
            if self.level.value == 1 and re.search(r'\b(two pointers?|sliding window|binary search|monotonic stack|hash ?map|depth.first|breadth.first|dynamic programming|kadane|union.find)\b', visible, re.I):
                raise ValueError('Level 1 must not name the algorithm or pattern')
            if self.level.value == 2:
                if len(self.guidance) > 600 or re.search(
                    r'\bif\b[^.!?\n]{0,200}\b(?:sum|total)\b[^.!?\n]{0,200}\b(?:mov\w*|increment\w*|decrement\w*)\b',
                    self.guidance, re.I):
                    raise ValueError('Level 2 must explain the pattern, not conditional update rules')
        elif self.level.value == 4:
            if not self.contains_code or not self.pseudocode or not self.pseudocode.strip():
                raise ValueError('Level 4 requires structured pseudocode')
            visible = ' '.join(filter(None, (self.title, self.guidance, self.pseudocode,
                                             self.guiding_question, self.explanation,
                                             self.time_complexity, self.space_complexity)))
            if self.code or has_code(visible):
                raise ValueError('Level 4 must not contain executable code')
        else:
            if not self.contains_code or not self.code or not self.explanation:
                raise ValueError('Level 5 requires code and explanation')
            if not self.time_complexity or not self.space_complexity:
                raise ValueError('Level 5 requires time and space complexity')
        return self


def has_code(text: str) -> bool:
    return bool(re.search(r'#include|\b(?:int|bool|void|auto|vector\s*<[^>]+>)\s+\w+\s*(?:[=(;])|\breturn\s+[^\n;]+;|\b(?:for|while)\s*\([^\n]+\)|\bdef\s+\w+\s*\(', text))


class MistakeDiagnosisResponse(BaseModel):
    """Structured response diagnosing student code failure."""
    category: MistakeCategory = Field(description="Classified category of the student's conceptual mistake.")
    misconception_summary: str = Field(
        description="1-2 sentences explaining what underlying conceptual misunderstanding likely caused this error."
    )
    guiding_question: str = Field(
        description="A targeted Socratic question that helps the student spot and fix their misconception without rewriting their code."
    )
    suggested_focus_area: str = Field(
        description="Specific concept or line/loop invariant for the student to examine."
    )

    @model_validator(mode='after')
    def validate_diagnosis(self):
        fields = (self.misconception_summary, self.guiding_question, self.suggested_focus_area)
        if any(len(text.strip()) < 5 for text in fields):
            raise ValueError('Diagnosis fields must be meaningful nonempty text')
        if has_code(' '.join(fields)):
            raise ValueError('Diagnosis must guide, not rewrite executable code')
        return self


class BenchmarkMetrics(BaseModel):
    """Empirical measurements for model performance."""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_duration_ms: float
    load_duration_ms: float
    prompt_eval_duration_ms: float
    eval_duration_ms: float
    tokens_per_second: float
    gpu_vram_used_mb: Optional[float] = None
    system_ram_used_mb: Optional[float] = None


class ReflectionAspect(str, Enum):
    """The conceptual dimension being probed in a reflection question."""
    INVARIANT = "invariant"
    COMPLEXITY = "complexity"
    EDGE_CASE = "edge_case"
    FOLLOW_UP = "follow_up"


class ReflectionQuestion(BaseModel):
    """A single post-AC reflection question generated by the tutor."""
    aspect: ReflectionAspect = Field(description="Which conceptual dimension is being probed.")
    question: str = Field(description="A clear, specific question for the student to reflect on.")
    context_hint: Optional[str] = Field(
        default=None,
        description="Optional brief context (1 sentence) to frame the question without answering it."
    )


class ReflectionFeedback(BaseModel):
    """Tutor's constructive feedback on a student's reflection answer."""
    is_correct_direction: bool = Field(
        description="True if the student's reasoning is broadly on the right track."
    )
    feedback: str = Field(
        description="2-3 sentences of constructive feedback. Does not reveal the full answer directly."
    )
    follow_up_question: Optional[str] = Field(
        default=None,
        description="Optional probing follow-up question if the answer was incomplete."
    )
