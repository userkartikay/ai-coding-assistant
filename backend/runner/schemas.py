"""Schemas for trusted C++ compilation, test execution, and deterministic judging."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TestVerdict(str, Enum):
    __test__ = False
    AC = "AC"                    # Passed the available verified suite, not a universal proof
    WA = "WA"                    # Wrong Answer (output did not match expected)
    TLE = "TLE"                  # Time Limit Exceeded
    RUNTIME_ERROR = "RUNTIME_ERROR"  # Non-zero exit code / crash / segfault
    COMPILATION_ERROR = "COMPILATION_ERROR"  # Failed to compile with g++
    OUTPUT_LIMIT = "OUTPUT_LIMIT"
    MEMORY_LIMIT = "MEMORY_LIMIT"


class TestCase(BaseModel):
    """A single deterministic test case."""
    __test__ = False
    id: str
    input_data: str = Field(description="Standard input passed to the program.")
    expected_output: str = Field(description="Expected standard output.")
    is_hidden: bool = Field(default=False, description="True for hidden edge cases.")


class TestCaseResult(BaseModel):
    """Outcome of running a single test case."""
    __test__ = False
    test_case_id: str
    passed: bool
    verdict: TestVerdict
    actual_output: Optional[str] = None
    expected_output: Optional[str] = None
    input_data: Optional[str] = None
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


class ExecutionReport(BaseModel):
    """Complete summary of compilation and test execution."""
    overall_verdict: TestVerdict
    compilation_success: bool
    compilation_output: str = ""
    compilation_time_ms: float = 0.0
    test_results: List[TestCaseResult] = Field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failing_evidence: Optional[str] = Field(
        default=None,
        description="Formatted evidence of first failure, ready for Socratic tutor."
    )
