"""Curriculum data models and pattern taxonomy schemas."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Provenance(str, Enum):
    USER_REPO = "user_repo"        # Sourced from user's leetcode-solutions repository
    CURATED_CORE = "curated_core"  # Curated to bridge key syllabus blind spots


class VerificationStatus(str, Enum):
    VERIFIED = "verified"          # Driver harness, canonical code, and test suite fully verified
    PLANNED = "planned"            # Scheduled for verification in Phase 2
    REVIEWED = "reviewed"          # User solution reviewed and catalogued


class CurriculumProblem(BaseModel):
    __test__ = False
    leetcode_id: int = Field(gt=0, strict=True)
    title: str
    difficulty: Difficulty
    primary_pattern: str
    subpattern: str
    secondary_patterns: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    time_complexity_target: str
    space_complexity_target: str
    educational_utility: str
    provenance: Provenance
    previously_solved_by_user: bool = False
    user_solution_reviewed: bool = False
    verification_status: VerificationStatus = VerificationStatus.PLANNED
    common_misconceptions: List[str] = Field(default_factory=list)
    official_link: str
