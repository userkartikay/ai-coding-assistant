import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from './api'
import { readSession, saveSession } from './storage'
import type { MentorSession, Problem } from './types'
import Icon from './Icon'

const levels = ['Conceptual nudge', 'Recognize the pattern', 'Algorithmic direction', 'Structured pseudocode', 'Explained solution']

export default function Mentor({ problem }: { problem: Problem }) {
  const [open, setOpen] = useState(true)
  const [session, setSession] = useState<MentorSession | null>(null)
  const [restoring, setRestoring] = useState(() => Boolean(readSession(problem.id)))
  const [selected, setSelected] = useState(1)
  const [error, setError] = useState('')
  const [started, setStarted] = useState<number | null>(null)
  const [now, setNow] = useState(Date.now)
  const [consent, setConsent] = useState(false)
  const alive = useRef(true)
  useEffect(() => {
    alive.current = true
    const saved = readSession(problem.id)
    if (saved && problem.executable) {
      api.session(saved).then(value => {
        if (!alive.current) return
        setSession(value); setSelected(value.unlocked_level || 1); setRestoring(false)
      }).catch(() => {
        if (alive.current) { setRestoring(false); setError('The previous mentor session is unavailable. Request a hint to start again. Your draft is safe.') }
      })
    }
    return () => { alive.current = false }
  }, [problem.id, problem.executable])
  useEffect(() => {
    if (started === null) return
    const interval = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(interval)
  }, [started])
  const unlocked = session?.unlocked_level ?? 0
  const hint = session?.hints[String(selected)]
  const busy = started !== null || restoring
  async function requestHint() {
    setError(''); setStarted(Date.now())
    try {
      const active = session ?? await api.newSession(problem.id)
      saveSession(problem.id, active.id)
      if (!alive.current) return
      setSession(active)
      const next = await api.hint(active.id, selected)
      if (alive.current) setSession(next)
    } catch (err) {
      if (alive.current) {
        if (err instanceof ApiError && (err.status === 410 || err.status === 403)) {
          setSession(null); setSelected(1)
          if (err.status === 403) await api.bootstrap().catch(() => undefined)
          setError('The local mentor session was reset. Retry from level 1; your draft is unaffected.')
        } else setError(err instanceof Error ? err.message : 'The mentor could not respond. Retry this level.')
      }
    } finally { if (alive.current) setStarted(null) }
  }
  return <section className="mentor panel-section" aria-label="Socratic AI mentor">
    <button className="section-heading" onClick={() => setOpen(!open)} aria-expanded={open}>
      <span><span className="section-icon mint"><Icon name="spark" /></span> Socratic mentor <span className="quiet-badge">Qwen 3.5 · 4B</span></span>
      <Icon name="chevron" />
    </button>
    {open && <div className="section-content">
      {!problem.executable ? <div className="empty-state"><Icon name="book" /><h3>A grounded statement comes first.</h3><p>This question has catalogue metadata, but no verified statement or constraints yet. AI hints are unavailable until that content is added.</p></div> : <>
        <div className="mentor-intro"><span className="eyebrow">A LITTLE HELP, ONE STEP AT A TIME</span><p>Build the idea yourself. Start with a question, not a solution.</p></div>
        <div className="hint-steps" aria-label="Progressive hint levels">
          {levels.map((label, i) => <button key={label} className={`hint-step ${selected === i + 1 ? 'active' : ''} ${i + 1 <= unlocked ? 'unlocked' : ''}`}
            disabled={busy || i + 1 > unlocked + 1} onClick={() => { setSelected(i + 1); setError('') }} aria-label={`Level ${i + 1}: ${label}`} aria-pressed={selected === i + 1} title={label}>
            <span>{i + 1 <= unlocked ? <Icon name="check" size={13} /> : i + 1}</span><small>{['Nudge', 'Pattern', 'Strategy', 'Pseudocode', 'Solution'][i]}</small>
          </button>)}
        </div>
        <div className="hint-label"><strong>Level {selected} · {levels[selected - 1]}</strong><span>{unlocked}/5 unlocked</span></div>
        {hint && !busy ? <article className="hint-output"><span className="eyebrow">AI GUIDANCE · NOT A JUDGE VERDICT</span><h3>{hint.title}</h3><p className="preserve-lines">{hint.guidance}</p>
          {hint.guiding_question && <blockquote><Icon name="spark" size={16} /><p>{hint.guiding_question}</p></blockquote>}
          {hint.pseudocode && <pre>{hint.pseudocode}</pre>}{hint.code && <pre>{hint.code}</pre>}
          {hint.explanation && <p className="preserve-lines">{hint.explanation}</p>}
          {hint.time_complexity && <p><b>Time:</b> {hint.time_complexity}</p>}{hint.space_complexity && <p><b>Space:</b> {hint.space_complexity}</p>}
        </article> : !busy && !error ? <div className="hint-placeholder"><Icon name="spark" size={23} /><p>{selected === 1 ? 'What do the input properties make possible?' : `Ready for ${levels[selected - 1].toLowerCase()}?`}</p><small>Request this level when you need it.</small></div> : null}
        {busy && <div className="generation-state" role="status"><span className="status-dot" /><div><strong>{restoring ? 'Restoring mentor session…' : `Generating locally · ${Math.max(0, Math.floor((now - (started ?? now)) / 1000))}s`}</strong><p>Waiting for a complete, validated response. This model can take a minute or more.</p></div></div>}
        {error && <div className="error-message" role="alert"><Icon name="alert" /><div><strong>Hint not unlocked</strong><p>{error}</p></div></div>}
        {selected === 5 && !hint && <label className="solution-consent"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} /> I’m ready to reveal the complete explained solution.</label>}
        {!hint && <button className="primary-button mentor-request" disabled={busy || (selected === 5 && !consent)} onClick={() => void requestHint()}><Icon name={error ? 'refresh' : 'spark'} />{error ? 'Retry this hint' : `Request level ${selected} hint`}</button>}
        <p className="fine-print">Hints are AI-generated. Check the reasoning; structural validation does not prove it correct. No raw token streaming is available in this MVP.</p>
      </>}
    </div>}
  </section>
}
