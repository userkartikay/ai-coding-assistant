import { describe, expect, it } from 'vitest'
import { filterQuestions, questionLabel, sortQuestions } from './catalogue'
import type { Question } from './types'
const questions: Question[] = [
  { id: 'lc_167', leetcode_id: 167, title: 'Two Sum II - Input Array Is Sorted', difficulty: 'Medium', pattern: 'Two Pointers', subpattern: 'Opposite ends', executable: true, provenance: 'user_repo' },
  { id: 'lc_1', leetcode_id: 1, title: 'Two Sum', difficulty: 'Easy', pattern: 'Hash Table', subpattern: 'Complement lookup', executable: false, provenance: 'curated_core' },
  { id: 'lc_704', leetcode_id: 704, title: 'Binary Search', difficulty: 'Easy', pattern: 'Binary Search', subpattern: 'Exact target', executable: true, provenance: 'user_repo' },
]
describe('official question identities', () => {
  it('formats official numbers without artificial numbering or zero padding', () => {
    expect(questionLabel(questions[0])).toBe('#167 — Two Sum II - Input Array Is Sorted')
    expect(questionLabel(questions[1])).toBe('#1 — Two Sum')
  })
  it.each([['#167',167],['704',704],['Two Sum II',167],['two pointers',167],['complement',1]])('searches %s', (query, number) => {
    expect(filterQuestions(questions, String(query), '', '', '', 'independent').map(q => q.leetcode_id)).toEqual([number])
  })
  it('sorts numbers numerically, difficulties by rank and topics alphabetically with numeric ties', () => {
    expect(sortQuestions(questions,'number').map(q => q.leetcode_id)).toEqual([1,167,704])
    expect(sortQuestions(questions,'difficulty').map(q => q.leetcode_id)).toEqual([1,704,167])
    expect(sortQuestions(questions,'topic').map(q => q.leetcode_id)).toEqual([704,1,167])
    expect(questions.map(q => q.leetcode_id)).toEqual([167,1,704])
  })
})
