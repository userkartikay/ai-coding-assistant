import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import LearnDSA from './LearnDSA'
import Review from './Review'
import { api } from './api'
import type { Lesson, Question, Problem, SolutionReview } from './types'

vi.mock('./api', () => ({ ApiError: class extends Error {}, api: { lessons: vi.fn(), askLesson: vi.fn(), review: vi.fn(), bootstrap: vi.fn() } }))
const question: Question = { id: 'lc_704', leetcode_id: 704, title: 'Binary Search', difficulty: 'Easy', pattern: 'Binary Search', subpattern: 'Exact search', executable: true, provenance: 'curated_core' }
const lesson: Lesson = { id: 'binary-search', title: 'Binary Search', introduction: 'Search ordered data.', intuition: 'Discard only impossible candidates.', stl: ['lower_bound(a.begin(), a.end(), target);'], template: '// Reviewed lower bound template', complexity: 'O(log N) time, O(1) space.', subpatterns: [{ name: 'Lower bound', distinction: 'Find the first possible position.' }], recognition_questions: ['Is the predicate monotonic?'], misconceptions: ['Check bounds before indexing.'], related_questions: [704], walkthrough: [{ values: ['1','3','5'], active: [1], links: [], note: 'Compare the middle entry.' }, { values: ['1','3','5'], active: [2], links: [], note: 'The remaining boundary is index 2.' }], diagram: 'array', review_status: 'starter_content_reviewed' }
const problem: Problem = { id: 'lc_704', executable: true, metadata: { leetcode_id: 704, title: 'Binary Search', difficulty: 'Easy', primary_pattern: 'Binary Search', subpattern: 'Exact search', secondary_patterns: [], prerequisites: [], time_complexity_target: 'O(log N)', space_complexity_target: 'O(1)', educational_utility: 'Search ordered data.', common_misconceptions: [], official_link: 'https://leetcode.com/problems/binary-search/', provenance: 'curated_core' }, description: 'Find a target.', constraints: 'Sorted input.', function_signature: 'int search(vector<int>& nums, int target)', starter_code: '', test_count: 1, examples: [] }
const feedback: SolutionReview = { mode: 'approach', evidence: 'not_executed', identified_pattern: 'Boundary search', invariant: 'The possible answer stays inside the range.', estimated_time: 'O(log N)', estimated_space: 'O(1)', observations: ['Check the missing-target boundary.'], edge_cases: ['Target greater than every entry.'], simplification: 'Keep a single interval convention.', alternatives: [], uncertainty: 'Static review without execution evidence.', guiding_question: 'Which interval endpoints remain possible?' }
beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.lessons).mockResolvedValue([lesson])
  vi.mocked(api.askLesson).mockResolvedValue({ source: 'ai_lesson', feedback: { lesson_id: lesson.id, answer: 'The insertion position may equal size.', material_sections: ['template'], uncertainty: 'Assumes sorted input.', guiding_question: 'What happens when the target is absent?' } })
  vi.mocked(api.review).mockResolvedValue({ source: 'ai_review', student_code_executed: false, feedback })
})
it('navigates lesson subpatterns, reviewed states and officially numbered practice links', async () => {
  const user = userEvent.setup(); const practice = vi.fn()
  render(<LearnDSA questions={[question]} practice={practice} selected={lesson.id} onSelect={vi.fn()} />)
  expect(await screen.findByRole('heading', { name: 'Binary Search', level: 1 })).toBeInTheDocument()
  expect(screen.getByText('Lower bound')).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Next step' }))
  expect(screen.getByText('The remaining boundary is index 2.')).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: /#704 — Binary Search/ }))
  expect(practice).toHaveBeenCalledWith('lc_704')
})
it('labels AI follow-up separately and retries without replacing reviewed material', async () => {
  const user = userEvent.setup()
  vi.mocked(api.askLesson).mockRejectedValueOnce(new Error('Mentor timeout'))
  render(<LearnDSA questions={[question]} practice={vi.fn()} selected={lesson.id} onSelect={vi.fn()} />)
  await screen.findByRole('heading', { name: 'Binary Search', level: 1 })
  await user.type(screen.getByLabelText('Lesson follow-up question'), 'Why check bounds?')
  await user.click(screen.getByRole('button', { name: 'Ask local mentor' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Mentor timeout')
  expect(screen.getByText(lesson.intuition)).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Retry lesson question' }))
  expect(await screen.findByText('AI LESSON FOLLOW-UP')).toBeInTheDocument()
  expect(api.askLesson).toHaveBeenLastCalledWith('binary-search','Why check bounds?')
})
it('keeps Hint Only as default and requires consent for optional review', async () => {
  const user = userEvent.setup(); render(<Review problem={problem} code="// draft" />)
  await user.click(screen.getByText('Review my solution'))
  expect(screen.getByLabelText('Solution assistance mode')).toHaveValue('hint')
  expect(api.review).not.toHaveBeenCalled()
  await user.selectOptions(screen.getByLabelText('Solution assistance mode'),'approach')
  expect(screen.getByRole('button', { name: 'Request solution review' })).toBeDisabled()
  await user.click(screen.getByRole('checkbox'))
  await user.click(screen.getByRole('button', { name: 'Request solution review' }))
  expect(await screen.findByText('AI SUGGESTIONS · NOT A JUDGE VERDICT')).toBeInTheDocument()
  expect(api.review).toHaveBeenCalledWith('lc_704','// draft','approach')
})
it('compares alternatives with tradeoffs only after opt-in and marks edited snapshots', async () => {
  const user = userEvent.setup()
  vi.mocked(api.review).mockResolvedValue({ source: 'ai_review', student_code_executed: false, feedback: { ...feedback, mode: 'compare', alternatives: [{ name: 'Linear scan', direction: 'Inspect each value once.', estimated_time: 'O(N)', estimated_space: 'O(1)', tradeoff: 'Works without sorted input.' }, { name: 'Hash index', direction: 'Build a reusable lookup.', estimated_time: 'O(N) build', estimated_space: 'O(N)', tradeoff: 'Extra memory enables repeated queries.' }] } })
  const view = render(<Review problem={problem} code="// first" />)
  await user.click(screen.getByText('Review my solution')); await user.selectOptions(screen.getByLabelText('Solution assistance mode'),'compare'); await user.click(screen.getByRole('checkbox')); await user.click(screen.getByRole('button', { name: 'Request solution review' }))
  expect(await screen.findByText('Linear scan')).toBeInTheDocument()
  expect(screen.getByText('Extra memory enables repeated queries.')).toBeInTheDocument()
  view.rerender(<Review problem={problem} code="// edited" />)
  expect(screen.getByText(/Feedback belongs to the earlier snapshot/)).toBeInTheDocument()
})
it('shows review failures without fabricated feedback and allows retry', async () => {
  const user = userEvent.setup();vi.mocked(api.review).mockRejectedValueOnce(new Error('Invalid response'))
  render(<Review problem={problem} code="// draft" />)
  await user.click(screen.getByText('Review my solution')); await user.selectOptions(screen.getByLabelText('Solution assistance mode'),'approach'); await user.click(screen.getByRole('checkbox')); await user.click(screen.getByRole('button', { name: 'Request solution review' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid response')
  expect(screen.queryByText('AI SUGGESTIONS · NOT A JUDGE VERDICT')).not.toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Retry solution review' }))
  expect(await screen.findByText('Boundary search')).toBeInTheDocument()
})
it('disables review for catalogue-only questions', async () => {
  const user = userEvent.setup();render(<Review problem={{ ...problem, executable: false }} code="// draft" />)
  await user.click(screen.getByText('Review my solution'));await user.selectOptions(screen.getByLabelText('Solution assistance mode'),'compare')
  expect(screen.getByText(/Review is pending verified statement grounding/)).toBeInTheDocument()
  expect(within(screen.getByText('Review my solution').closest('details')!).queryByRole('checkbox')).not.toBeInTheDocument()
})
