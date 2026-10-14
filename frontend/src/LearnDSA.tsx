import { useEffect, useState } from 'react'
import { api, ApiError } from './api'
import { questionLabel } from './catalogue'
import type { Lesson, LessonAnswer, Question } from './types'

function Walkthrough({ lesson }: { lesson: Lesson }) {
  const [index, setIndex] = useState(0)
  const step = lesson.walkthrough[index]
  const count = Math.max(1, step.values.length)
  const positions = lesson.id === 'trees-bst' ? [[100,35],[50,115],[150,115]]
    : lesson.id === 'graphs' ? [[50,40],[150,40],[50,120],[150,120]]
      : step.values.map((_, i) => [i * 100 + 50,65])
  const branching = ['trees-bst','graphs'].includes(lesson.id)
  return <section className="walkthrough"><h3>Annotated walkthrough</h3><p className="fine-print">Reviewed example states · use the controls to follow the invariant.</p>
    {lesson.diagram === 'graph' ? <svg role="img" aria-label={`${lesson.title} walkthrough state ${index + 1}`} viewBox={`0 0 ${branching ? 200 : count * 100} ${branching ? 160 : 130}`}>
      <defs><marker id={`arrow-${lesson.id}`} markerWidth="8" markerHeight="8" refX="18" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="currentColor" /></marker></defs>
      {step.links.map(([a, b]) => <line key={`${a}-${b}`} x1={positions[a][0]} y1={positions[a][1]} x2={positions[b][0]} y2={positions[b][1]} stroke="currentColor" markerEnd={`url(#arrow-${lesson.id})`} />)}
      {step.values.map((value, i) => <g key={i}><circle cx={positions[i][0]} cy={positions[i][1]} r="25" className={step.active.includes(i) ? 'active-node' : 'diagram-node'} /><text x={positions[i][0]} y={positions[i][1] + 5} textAnchor="middle" fill="currentColor">{value}</text></g>)}
    </svg> : <div className={`state-cells ${lesson.diagram === 'stack' ? 'stack-cells' : ''}`} aria-label="Walkthrough values">{step.values.length ? step.values.map((value, i) => <div className={step.active.includes(i) ? 'active-cell' : ''} key={i}><strong>{value}</strong><small>{lesson.diagram === 'stack' ? i === step.values.length - 1 ? 'top' : 'bottom' : `index ${i}`}</small></div>) : <p>Empty stack</p>}</div>}
    <p aria-live="polite">{step.note}</p><div className="step-controls"><button className="secondary-button" disabled={index === 0} onClick={() => setIndex(index - 1)}>Previous step</button><span>Step {index + 1} / {lesson.walkthrough.length}</span><button className="secondary-button" disabled={index === lesson.walkthrough.length - 1} onClick={() => setIndex(index + 1)}>Next step</button></div>
  </section>
}

function LessonView({ lesson, questions, practice }: { lesson: Lesson; questions: Question[]; practice: (id: string) => void }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<LessonAnswer | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function ask() {
    setBusy(true); setError(''); setAnswer(null)
    try { const response = await api.askLesson(lesson.id, question); setAnswer(response.feedback) }
    catch (err) { if (err instanceof ApiError && err.status === 403) await api.bootstrap().catch(() => {}); setError(err instanceof Error ? err.message : 'Lesson mentor unavailable.') }
    finally { setBusy(false) }
  }
  return <article className="lesson-content"><span className="eyebrow">LEARN → UNDERSTAND → PRACTICE → REVISE</span><h1>{lesson.title}</h1><p>{lesson.introduction}</p>
    <h2>Intuition</h2><p>{lesson.intuition}</p><h2>Subpatterns</h2><div className="subpattern-grid">{lesson.subpatterns.map(s => <article key={s.name}><h3>{s.name}</h3><p>{s.distinction}</p></article>)}</div>
    <h2>Recognize the approach</h2><ul>{lesson.recognition_questions.map(q => <li key={q}>{q}</li>)}</ul>
    <Walkthrough key={lesson.id} lesson={lesson} />
    <h2>C++ toolbox</h2>{lesson.stl.map(s => <pre className="signature" key={s}>{s}</pre>)}<details className="lesson-template"><summary>Study the reusable template</summary><p className="fine-print">Illustrates one subpattern; check its assumptions and adapt the node/input types.</p><pre>{lesson.template}</pre></details>
    <h2>Complexity and assumptions</h2><p>{lesson.complexity}</p><h2>Mistakes and edge cases</h2><ul>{lesson.misconceptions.map(m => <li key={m}>{m}</li>)}</ul>
    <h2>Related practice</h2><p>Practice remains optional. Your current practice mode and drafts are preserved.</p><div className="related-questions">{lesson.related_questions.map(n => questions.find(q => q.leetcode_id === n)).filter((q): q is Question => !!q).map(q => <button className="secondary-button" key={q.id} onClick={() => practice(q.id)}>{questionLabel(q)}<small>{q.executable ? 'Verified suite' : 'Catalogue only'}</small></button>)}</div>
    <section className="lesson-mentor"><h2>Ask about this lesson</h2><p className="fine-print">Qwen receives only this lesson and your question. AI explanations require judgment; they are separate from the reviewed starter material.</p>
      <label>Your follow-up<textarea aria-label="Lesson follow-up question" maxLength={800} value={question} disabled={busy} onChange={e => setQuestion(e.target.value)} /></label><button className="primary-button" disabled={busy || question.trim().length < 5} onClick={() => void ask()}>{busy ? 'Thinking about this lesson…' : error ? 'Retry lesson question' : 'Ask local mentor'}</button>
      {busy && <p role="status">Waiting for validated lesson feedback…</p>}{error && <p className="error-message" role="alert">{error}</p>}
      {answer && <div className="lesson-answer"><span className="eyebrow">AI LESSON FOLLOW-UP</span><p>{answer.answer}</p><p className="fine-print">Material sections: {answer.material_sections.join(', ')}</p><p>{answer.uncertainty}</p><p className="guiding-question">{answer.guiding_question}</p></div>}
    </section>
  </article>
}

export default function LearnDSA({ questions, practice, selected, onSelect }: { questions: Question[]; practice: (id: string) => void; selected: string; onSelect: (id: string) => void }) {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  useEffect(() => { let active = true; api.lessons().then(data => { if (active) { setLessons(data); setError('') } }).catch(err => { if (active) setError(err instanceof Error ? err.message : 'Lessons unavailable.') }); return () => { active = false } }, [retry])
  const lesson = lessons.find(l => l.id === selected) ?? lessons[0]
  return <div className="learning-workspace"><nav className="lesson-navigation" aria-label="DSA topics"><h2>Learn DSA</h2><p>Reviewed starter lessons.<br />Choose a topic, then practice.</p>{lessons.map(l => <button key={l.id} className={l.id === lesson?.id ? 'selected' : ''} aria-current={l.id === lesson?.id ? 'page' : undefined} onClick={() => onSelect(l.id)}>{l.title}<small>{l.subpatterns.length} subpatterns</small></button>)}</nav>
    {error ? <div role="alert"><p>{error}</p><button onClick={() => setRetry(retry + 1)}>Retry lessons</button></div> : lesson ? <LessonView key={lesson.id} lesson={lesson} questions={questions} practice={practice} /> : <p role="status">Loading reviewed lessons…</p>}
  </div>
}
