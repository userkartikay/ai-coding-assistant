import type { MentorSession, Problem, Question, ReferenceResults, MockResults, Lesson, LessonAnswer, SolutionReview } from './types'

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message) }
}
let token = ''
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', 'X-Mentor-Token': token, ...options.headers },
  })
  const body = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, typeof body?.detail === 'string' ? body.detail : `Request failed (${response.status}).`)
  return body as T
}
export const api = {
  async bootstrap() { const value = await request<{ token: string }>('/bootstrap'); token = value.token },
  health: () => request<{ tutor_available: boolean; model: string }>('/health'),
  questions: () => request<Question[]>('/problems'),
  lessons: () => request<Lesson[]>('/lessons'),
  askLesson: (id: string, question: string) => request<{ source: 'ai_lesson'; feedback: LessonAnswer }>(`/lessons/${encodeURIComponent(id)}/questions`, { method: 'POST', body: JSON.stringify({ question }) }),
  review: (id: string, code: string, mode: 'approach' | 'compare') => request<{ source: 'ai_review'; student_code_executed: false; feedback: SolutionReview }>('/reviews', { method: 'POST', body: JSON.stringify({ problem_id: id, code, mode, reveal_teaching_details: true }) }),
  problem: (id: string) => request<Problem>(`/problems/${encodeURIComponent(id)}`),
  newSession: (id: string) => request<MentorSession>('/sessions', { method: 'POST', body: JSON.stringify({ problem_id: id }) }),
  session: (id: string) => request<MentorSession>(`/sessions/${encodeURIComponent(id)}`),
  hint: (id: string, level: number) => request<MentorSession>(`/sessions/${encodeURIComponent(id)}/hints`, { method: 'POST', body: JSON.stringify({ level }) }),
  references: (id: string) => request<ReferenceResults>(`/problems/${encodeURIComponent(id)}/reference-results`),
  mock: (id: string, scenario: string) => request<MockResults>(`/problems/${encodeURIComponent(id)}/mock-results?scenario=${encodeURIComponent(scenario)}`),
}
