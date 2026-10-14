import type { Mode, Question } from './types'
export function filterQuestions(questions: Question[], query: string, difficulty: string, pattern: string, subpattern: string, mode: Mode) {
  const search = query.trim().toLowerCase().replace(/^#/, '')
  return questions.filter(q => (`${q.leetcode_id} ${q.title} ${q.pattern} ${q.subpattern}`.toLowerCase().includes(search))
    && (!difficulty || q.difficulty === difficulty)
    && (mode === 'independent' || ((!pattern || q.pattern === pattern) && (!subpattern || q.subpattern === subpattern))))
}

export type SortOrder = 'number' | 'difficulty' | 'topic'
export function questionLabel(q: { leetcode_id: number; title: string }) { return `#${q.leetcode_id} — ${q.title}` }
export function sortQuestions(questions: Question[], order: SortOrder) {
  const ranks: Record<string, number> = { Easy: 0, Medium: 1, Hard: 2 }
  return [...questions].sort((a, b) => (order === 'difficulty' ? ranks[a.difficulty] - ranks[b.difficulty]
    : order === 'topic' ? a.pattern.localeCompare(b.pattern) : 0) || a.leetcode_id - b.leetcode_id)
}
