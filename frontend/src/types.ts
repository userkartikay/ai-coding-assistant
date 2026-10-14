export type Mode = 'independent' | 'guided'
export type Theme = 'dark' | 'light'
export interface Question {
  id: string; leetcode_id: number; title: string; difficulty: string
  pattern: string; subpattern: string; executable: boolean; provenance: string
}
export interface Problem {
  id: string; executable: boolean; description: string | null; constraints: string | null
  function_signature: string | null; starter_code: string; test_count: number
  examples: { id: string; input_data: string; expected_output: string }[]
  metadata: {
    leetcode_id: number; title: string; difficulty: string; primary_pattern: string
    subpattern: string; secondary_patterns: string[]; prerequisites: string[]
    time_complexity_target: string; space_complexity_target: string
    educational_utility: string; common_misconceptions: string[]; official_link: string; provenance: string
  }
}
export interface Hint {
  level: number; title: string; guidance: string; guiding_question: string | null
  code: string | null; pseudocode: string | null; explanation: string | null
  time_complexity: string | null; space_complexity: string | null
}
export interface MentorSession { id: string; problem_id: string; unlocked_level: number; hints: Record<string, Hint> }
export interface TestResult {
  test_case_id: string; passed: boolean; verdict: string; input_data: string | null
  expected_output: string | null; actual_output: string | null; error_message: string | null
  execution_time_ms: number; truncated_fields?: string[]
}
export interface JudgeReport {
  overall_verdict: string; compilation_success: boolean; compilation_output: string
  compilation_time_ms: number; total_tests: number; passed_tests: number
  test_results: TestResult[]; failing_evidence: string | null
}
export interface ReferenceResults {
  source: 'trusted_reference'; student_code_executed: false; recorded_at: string
  reports: { canonical: JudgeReport; known_bug: JudgeReport }
}
export interface MockResults { source: 'mock'; student_code_executed: false; report: JudgeReport }

export interface Lesson {
  id: string; title: string; introduction: string; intuition: string; stl: string[]; template: string
  complexity: string; subpatterns: { name: string; distinction: string }[]
  recognition_questions: string[]; misconceptions: string[]; related_questions: number[]
  walkthrough: { note: string; values: string[]; active: number[]; links: [number, number][] }[]
  diagram: string; review_status: string
}
export interface LessonAnswer { lesson_id: string; answer: string; material_sections: string[]; uncertainty: string; guiding_question: string }
export interface SolutionReview {
  mode: 'approach' | 'compare'; evidence: 'not_executed'; identified_pattern: string; invariant: string
  estimated_time: string; estimated_space: string; observations: string[]; edge_cases: string[]
  simplification: string; uncertainty: string; guiding_question: string
  alternatives: { name: string; direction: string; estimated_time: string; estimated_space: string; tradeoff: string }[]
}
