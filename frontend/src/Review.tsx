import { useState } from 'react'
import { api, ApiError } from './api'
import type { Problem, SolutionReview } from './types'

export default function Review({ problem, code }: { problem: Problem; code: string }) {
  const [mode, setMode] = useState<'hint' | 'approach' | 'compare'>('hint')
  const [consent, setConsent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState<SolutionReview | null>(null)
  const [reviewedCode, setReviewedCode] = useState('')
  async function review() {
    if (mode === 'hint') return
    const snapshot = code
    setBusy(true); setError(''); setFeedback(null)
    try { const response = await api.review(problem.id, snapshot, mode); setFeedback(response.feedback); setReviewedCode(snapshot) }
    catch (err) { if (err instanceof ApiError && err.status === 403) await api.bootstrap().catch(() => {}); setError(err instanceof Error ? err.message : 'Review unavailable.') }
    finally { setBusy(false) }
  }
  return <details className="review-panel"><summary>Review my solution <span className="quiet-badge">Optional AI feedback</span></summary>
    <label>Assistance mode<select aria-label="Solution assistance mode" disabled={busy} value={mode} onChange={e => { setMode(e.target.value as typeof mode); setFeedback(null); setConsent(false); setError('') }}><option value="hint">Hint Only</option><option value="approach">Review My Approach</option><option value="compare">Compare Alternative Solutions</option></select></label>
    {mode === 'hint' ? <p>Use the progressive mentor above. Hint Only preserves its five backend-enforced tiers.</p> : !problem.executable ? <p>Review is pending verified statement grounding for this catalogue-only question.</p> : <>
      <p className="fine-print">This experimental review reveals teaching details and analyses your draft through local Ollama. It can miss bugs or suggest incorrect concerns. It does not execute code, unlock hint tiers, or establish correctness.</p>
      <label className="consent"><input type="checkbox" checked={consent} disabled={busy} onChange={e => setConsent(e.target.checked)} /> I want pattern and complexity feedback beyond the hint ladder.</label>
      <button className="primary-button" disabled={busy || !consent || !code.trim() || code.length > 3500} onClick={() => void review()}>{busy ? 'Reviewing with the local mentor…' : error ? 'Retry solution review' : 'Request solution review'}</button>
      {code.length > 3500 && <p role="alert">Review supports up to 3,500 characters. Shorten the draft for this local model.</p>}
      {busy && <p role="status">Waiting for a complete validated response. No code is running.</p>}
      {error && <p className="error-message" role="alert">{error}</p>}
      {feedback && <div className="review-feedback"><span className="eyebrow">AI SUGGESTIONS · NOT A JUDGE VERDICT</span>
        <p className="practice-note">{code === reviewedCode ? 'Review of the requested draft snapshot. Draft not executed.' : 'You edited the draft after this review. Feedback belongs to the earlier snapshot.'}</p>
        <h3>{feedback.identified_pattern}</h3><p>{feedback.invariant}</p>
        <p><b>Estimated time:</b> {feedback.estimated_time}<br /><b>Estimated space:</b> {feedback.estimated_space}</p>
        <h4>Observations</h4><ul>{feedback.observations.map(x => <li key={x}>{x}</li>)}</ul>
        <h4>Edge cases to check</h4><ul>{feedback.edge_cases.map(x => <li key={x}>{x}</li>)}</ul><p><b>Simplification:</b> {feedback.simplification}</p>
        {feedback.alternatives.map(a => <article className="alternative" key={a.name}><h4>{a.name}</h4><p>{a.direction}</p><p>Estimated time {a.estimated_time} · Space {a.estimated_space}</p><p>{a.tradeoff}</p></article>)}
        <p><b>Uncertainty:</b> {feedback.uncertainty}</p><p className="guiding-question">{feedback.guiding_question}</p>
        <button className="secondary-button" onClick={() => document.querySelector<HTMLElement>('.monaco-editor textarea, textarea[aria-label="C++ code editor"]')?.focus()}>Revise this draft</button>
      </div>}
    </>}
  </details>
}
