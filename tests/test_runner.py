"""Automated test suite for trusted local C++ test runner and deterministic judge."""

import pytest
import os
from backend.runner.schemas import TestVerdict, TestCase
from backend.runner.cpp_runner import CppRunner


@pytest.fixture
def runner():
    return CppRunner(compile_timeout=4.0, test_timeout=1.5, max_output_bytes=1024)


def test_runner_success_ac(runner):
    """Test standard valid C++ solution passing all tests."""
    code = """#include <iostream>
int main() {
    int a, b;
    if (std::cin >> a >> b) {
        std::cout << (a + b) << std::endl;
    }
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc1", input_data="3 5\n", expected_output="8\n"),
        TestCase(id="tc2", input_data="-2 7\n", expected_output="5\n")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.compilation_success is True
    assert report.overall_verdict == TestVerdict.AC
    assert report.passed_tests == 2
    assert report.total_tests == 2
    assert report.failing_evidence is None


def test_runner_wrong_answer_wa(runner):
    """Test solution producing incorrect output."""
    code = """#include <iostream>
int main() {
    int a, b;
    if (std::cin >> a >> b) {
        std::cout << (a * b) << std::endl; // Wrong operation!
    }
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc1", input_data="3 5\n", expected_output="8\n")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.compilation_success is True
    assert report.overall_verdict == TestVerdict.WA
    assert report.passed_tests == 0
    assert report.failing_evidence is not None
    assert "Expected Output: 8" in report.failing_evidence
    assert "Actual Output: 15" in report.failing_evidence


def test_runner_compilation_error(runner):
    """Test syntax error failing compilation."""
    code = """#include <iostream>
int main() {
    this is invalid syntax !!!
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc1", input_data="1\n", expected_output="1\n")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.compilation_success is False
    assert report.overall_verdict == TestVerdict.COMPILATION_ERROR
    assert "error" in report.compilation_output.lower()
    assert report.failing_evidence is not None
    assert "COMPILATION ERROR" in report.failing_evidence


def test_runner_timeout_tle(runner):
    """Test infinite loop triggering TLE safeguard."""
    code = """#include <iostream>
int main() {
    while (true) {
        // infinite loop
    }
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc_tle", input_data="1\n", expected_output="1\n")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.compilation_success is True
    assert report.overall_verdict == TestVerdict.TLE
    assert report.passed_tests == 0
    assert report.failing_evidence is not None
    assert "Time Limit Exceeded (TLE)" in report.failing_evidence


def test_runner_runtime_error_rte(runner):
    """Test unhandled abort or non-zero exit code triggering RUNTIME_ERROR."""
    code = """#include <cstdlib>
int main() {
    exit(42); // Crash / exit non-zero
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc_rte", input_data="1\n", expected_output="1\n")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.compilation_success is True
    assert report.overall_verdict == TestVerdict.RUNTIME_ERROR
    assert report.failing_evidence is not None
    assert "Runtime Error (RTE)" in report.failing_evidence


def test_runner_bounded_output(runner):
    """Test output flooding is truncated at buffer limit."""
    code = """#include <iostream>
int main() {
    for (int i = 0; i < 5000; ++i) {
        std::cout << "VERY LONG OUTPUT THAT WOULD FLOOD MEMORY ";
    }
    std::cout << std::endl;
    return 0;
}
"""
    test_cases = [
        TestCase(id="tc_flood", input_data="", expected_output="short")
    ]
    report = runner.run_test_suite(code, test_cases, trusted=True)
    assert report.overall_verdict == TestVerdict.OUTPUT_LIMIT
    actual = report.test_results[0].actual_output
    assert "[Output truncated at buffer limit]" in actual
