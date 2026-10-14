import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { api, ApiError } from './api'
import type { MentorSession, Problem, Question } from './types'

vi.mock('./CodeEditor', () => ({ default: ({ value, onChange }: { value: string; onChange: (value: string) => void }) => <textarea aria-label="C++ code editor" value={value} onChange={e => onChange(e.target.value)} /> }))
vi.mock('./api', async importOriginal => ({ ...await importOriginal<typeof import('./api')>(), api: { bootstrap: vi.fn(), questions: vi.fn(), problem: vi.fn(), health: vi.fn(), references: vi.fn(), mock: vi.fn(), newSession: vi.fn(), session: vi.fn(), hint: vi.fn(), lessons: vi.fn(), askLesson: vi.fn(), review: vi.fn() } }))

const metadata = { leetcode_id: 167, title: 'Two Sum II - Input Array Is Sorted', difficulty: 'Medium', primary_pattern: 'Two Pointers', subpattern: 'Opposite-Directional (Collision)', secondary_patterns: [], prerequisites: [], time_complexity_target: 'O(N)', space_complexity_target: 'O(1)', educational_utility: 'Practice recognizing sorted pair structure.', common_misconceptions: [], official_link: 'https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/', provenance: 'user_repo' }
const first: Problem = { id: 'lc_167', executable: true, metadata, description: 'Find distinct indices with a target sum.', constraints: 'Array is sorted.', function_signature: 'vector<int> twoSum(vector<int>& numbers, int target)', starter_code: 'vector<int> twoSum(vector<int>& numbers, int target) {\n}\n', test_count: 1, examples: [{ id: 'ts2_1', input_data: '4\n2 7 11 15\n9', expected_output: '1 2' }] }
const second: Problem = { ...first, id: 'lc_56', executable: false, metadata: { ...metadata, leetcode_id: 56, title: 'Merge Intervals', primary_pattern: 'Intervals', subpattern: 'Sorting and overlap' }, description: null, constraints: null, function_signature: null, starter_code: '', test_count: 0, examples: [] }
const questions: Question[] = [first, second].map(p => ({ id: p.id, leetcode_id: p.metadata.leetcode_id, title: p.metadata.title, difficulty: p.metadata.difficulty, pattern: p.metadata.primary_pattern, subpattern: p.metadata.subpattern, executable: p.executable, provenance: p.metadata.provenance }))
const report = { overall_verdict: 'AC', compilation_success: true, compilation_output: '', compilation_time_ms: 10, total_tests: 1, passed_tests: 1, test_results: [], failing_evidence: null }
const unlocked: MentorSession = { id: 'session', problem_id: 'lc_167', unlocked_level: 1, hints: { '1': { level: 1, title: 'Consider the order', guidance: 'Think about the sorted input.', guiding_question: 'Which property can reduce repeated work?', code: null, pseudocode: null, explanation: null, time_complexity: null, space_complexity: null } } }

beforeEach(() => {
  vi.clearAllMocks(); localStorage.clear(); sessionStorage.clear()
  vi.mocked(api.bootstrap).mockResolvedValue(undefined)
  vi.mocked(api.questions).mockResolvedValue(questions)
  vi.mocked(api.problem).mockImplementation(async id => id === first.id ? first : second)
  vi.mocked(api.health).mockResolvedValue({ tutor_available: true, model: 'qwen3.5:4b' })
  vi.mocked(api.references).mockResolvedValue({ source: 'trusted_reference', student_code_executed: false, recorded_at: '2026-10-12T12:00:00Z', reports: { canonical: report, known_bug: { ...report, overall_verdict: 'WA', passed_tests: 0 } } })
  vi.mocked(api.newSession).mockResolvedValue({ id: 'session', problem_id: first.id, unlocked_level: 0, hints: {} })
  vi.mocked(api.hint).mockResolvedValue(unlocked)
  vi.mocked(api.mock).mockResolvedValue({ source: 'mock', student_code_executed: false, report: { ...report, overall_verdict: 'COMPILATION_ERROR', compilation_success: false, compilation_output: 'Illustrative compiler error.', passed_tests: 0 } })
})

it('moves from Learn DSA to official-number practice and restores the existing draft', async () => {
  const user = userEvent.setup()
  vi.mocked(api.lessons).mockResolvedValue([{ id: 'two-pointers', title: 'Two Pointers', introduction: 'Use ordered boundaries.', intuition: 'Eliminate impossible candidates.', stl: ['vector<int>'], template: '// Template', complexity: 'O(N)', subpatterns: [{ name: 'Opposite ends', distinction: 'Move one boundary with a proof.' }], recognition_questions: ['Is the input sorted?'], misconceptions: ['Avoid moving both boundaries.'], related_questions: [167], walkthrough: [{ values: ['2','7'], active: [0], links: [], note: 'Start.' }, { values: ['2','7'], active: [1], links: [], note: 'Finish.' }], diagram: 'array', review_status: 'starter_content_reviewed' }])
  await mount()
  await user.clear(screen.getByLabelText('C++ code editor'))
  await user.type(screen.getByLabelText('C++ code editor'),'// preserve during learning')
  await user.click(screen.getByRole('button', { name: 'Learn DSA' }))
  expect(await screen.findByRole('heading', { name: 'Two Pointers', level: 1 })).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: /#167 — Two Sum II/ }))
  expect(await screen.findByRole('heading', { name: `#167 — ${metadata.title}` })).toBeInTheDocument()
  expect(screen.getByLabelText('C++ code editor')).toHaveValue('// preserve during learning')
  expect(screen.getByRole('button', { name: 'Independent practice' })).toHaveAttribute('aria-pressed','true')
  expect(screen.queryByText('Time O(N)')).not.toBeInTheDocument()
})

async function mount() { const view = render(<App />); await screen.findByRole('heading', { name: `#167 — ${metadata.title}` }); await screen.findByRole('textbox', { name: 'C++ code editor' }); return view }

describe('student workspace', () => {
  it('defaults to independent practice without pattern or complexity disclosure', async () => {
    await mount()
    expect(screen.getByRole('button', { name: 'Independent practice' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.queryByLabelText('Pattern')).not.toBeInTheDocument()
    expect(screen.queryByText('Time O(N)')).not.toBeInTheDocument()
    expect(screen.queryByText(metadata.subpattern)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Run pending' })).toBeDisabled()
  })
  it('reveals metadata and filters only when guided learning is selected', async () => {
    const user = userEvent.setup(); await mount()
    await user.click(screen.getByRole('button', { name: 'Guided learning' }))
    expect(screen.getByText('Time O(N)')).toBeInTheDocument()
    await user.selectOptions(screen.getByLabelText('Pattern'), 'Intervals')
    expect(screen.getByRole('button', { name: /Merge Intervals/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /167.*Two Sum/ })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Independent practice' }))
    expect(screen.queryByLabelText('Pattern')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /167.*Two Sum/ })).toBeInTheDocument()
  })
  it('searches titles and distinguishes missing catalogue content', async () => {
    const user = userEvent.setup(); await mount()
    await user.type(screen.getByRole('textbox', { name: 'Search questions' }), 'merge')
    await user.click(screen.getByRole('button', { name: /Merge Intervals/ }))
    expect(await screen.findByText('Statement not yet available')).toBeInTheDocument()
    expect(screen.getByText('Constraints have not been catalogued for this question.')).toBeInTheDocument()
    expect(screen.getByText('A grounded statement comes first.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Request level 1 hint' })).not.toBeInTheDocument()
  })
  it('preserves drafts per question and restores after reload', async () => {
    const user = userEvent.setup(); const view = await mount()
    const editor = screen.getByRole('textbox', { name: 'C++ code editor' })
    await user.clear(editor); await user.type(editor, '// my independent attempt')
    await user.click(screen.getByRole('button', { name: /Merge Intervals/ }))
    await screen.findByRole('heading', { name: '#56 — Merge Intervals' })
    expect(screen.getByRole('textbox', { name: 'C++ code editor' })).toHaveValue('')
    await user.click(screen.getByRole('button', { name: /167.*Two Sum/ }))
    await screen.findByRole('heading', { name: `#167 — ${metadata.title}` })
    expect(screen.getByRole('textbox', { name: 'C++ code editor' })).toHaveValue('// my independent attempt')
    view.unmount(); await mount()
    expect(screen.getByRole('textbox', { name: 'C++ code editor' })).toHaveValue('// my independent attempt')
  })
  it('does not unlock the next tier after failure and supports retry', async () => {
    const user = userEvent.setup(); await mount()
    vi.mocked(api.hint).mockRejectedValueOnce(new Error('No level was unlocked.'))
    await user.click(screen.getByRole('button', { name: 'Request level 1 hint' }))
    expect(await screen.findByText('Hint not unlocked')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Level 2: Recognize the pattern' })).toBeDisabled()
    await user.click(screen.getByRole('button', { name: 'Retry this hint' }))
    expect(await screen.findByText('Consider the order')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Level 2: Recognize the pattern' })).toBeEnabled()
  })
  it('labels reference and mock compiler results without claiming to execute drafts', async () => {
    const user = userEvent.setup(); await mount()
    await user.click(screen.getByRole('button', { name: 'View results' }))
    expect(await screen.findByText(/Your draft has not been executed/)).toBeInTheDocument()
    expect(screen.getByText(/AC means this fixture passed/)).toBeInTheDocument()
    await user.selectOptions(screen.getByLabelText('Report source'), 'mock')
    expect(await screen.findByText(/MOCK PREVIEW/)).toBeInTheDocument()
    expect(await screen.findByText('Illustrative compiler error.')).toBeInTheDocument()
  })
  it('recovers an expired mentor session without unlocking an invalid tier', async () => {
    const user = userEvent.setup(); await mount()
    vi.mocked(api.hint).mockRejectedValueOnce(new ApiError(410, 'Session expired'))
    await user.click(screen.getByRole('button', { name: 'Request level 1 hint' }))
    expect(await screen.findByText(/local mentor session was reset/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Level 2: Recognize the pattern' })).toBeDisabled()
    await user.click(screen.getByRole('button', { name: 'Retry this hint' }))
    expect(await screen.findByText('Consider the order')).toBeInTheDocument()
    expect(api.newSession).toHaveBeenCalledTimes(2)
  })
  it('supports theme changes and keyboard panel resizing', async () => {
    const user = userEvent.setup(); await mount()
    await user.click(screen.getByRole('button', { name: 'Switch to light theme' }))
    expect(document.documentElement.dataset.theme).toBe('light')
    const divider = screen.getByRole('separator')
    divider.focus(); await user.keyboard('{ArrowRight}')
    expect(divider).toHaveAttribute('aria-valuenow', '43')
  })
  it('shows startup errors without replacing local drafts', async () => {
    localStorage.setItem('mentor:draft:lc_167', JSON.stringify({ code: '// keep me' }))
    vi.mocked(api.bootstrap).mockRejectedValueOnce(new Error('API offline'))
    render(<App />)
    expect(await screen.findByText('The local API is unavailable')).toBeInTheDocument()
    expect(JSON.parse(localStorage.getItem('mentor:draft:lc_167')!).code).toBe('// keep me')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Retry connection' })).toBeEnabled())
  })
})
