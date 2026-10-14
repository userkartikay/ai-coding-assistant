import { Component, lazy, Suspense, useState } from 'react'
import type { CSSProperties, ReactNode } from 'react'
import type { Mode, Problem, Theme } from './types'
import { loadDraft, saveDraft } from './storage'
import Icon from './Icon'
import Mentor from './Mentor'
import Results from './Results'
import Review from './Review'
import { questionLabel } from './catalogue'

const Editor = lazy(() => import('./CodeEditor'))
class EditorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  render() { return this.state.failed ? this.props.fallback : this.props.children }
}

export default function Workspace({ problem, theme, mode }: { problem: Problem; theme: Theme; mode: Mode }) {
  const [draft, setDraft] = useState(() => loadDraft(problem.id, problem.starter_code))
  const [split, setSplit] = useState(41)
  const [height, setHeight] = useState(340)
  const [resultsOpen, setResultsOpen] = useState(false)
  const [savedNotice, setSavedNotice] = useState('')
  function changeCode(value: string) { setDraft({ code: value, error: saveDraft(problem.id, value) }); setSavedNotice('') }
  function save() { const error = saveDraft(problem.id, draft.code); setDraft({ code: draft.code, error }); setSavedNotice(error ? '' : 'Draft saved on this device.') }
  function download() {
    const url = URL.createObjectURL(new Blob([draft.code], { type: 'text/plain' }))
    const link = document.createElement('a'); link.href = url; link.download = `${problem.id}.cpp`; link.click(); URL.revokeObjectURL(url)
  }
  const meta = problem.metadata
  return <div className="practice-workspace" style={{ '--problem-width': `${split}%` } as CSSProperties}>
    <article className="problem-pane">
      <div className="pane-toolbar"><span><Icon name="book" /> Problem</span><span className="quiet-badge">{mode === 'independent' ? 'Independent' : 'Guided'}</span></div>
      <div className="problem-content"><div className="problem-topline"><span className="eyebrow">PROBLEM {meta.leetcode_id}</span><a href={meta.official_link} target="_blank" rel="noreferrer" aria-label="Open original problem"><Icon name="external" size={15} /></a></div>
        <h1>{questionLabel(meta)}</h1><div className="problem-badges"><span className={`difficulty ${meta.difficulty.toLowerCase()}`}>{meta.difficulty}</span><span className={`availability ${problem.executable ? 'verified' : ''}`}>{problem.executable ? 'Verified suite' : 'Catalogue only'}</span></div>
        {mode === 'independent' ? <div className="practice-note"><Icon name="spark" /><p>Recognize the approach yourself. Pattern and complexity clues are hidden in this mode.</p></div> : <div className="teaching-metadata"><span className="eyebrow">LEARNING MAP</span><h3>{meta.primary_pattern}</h3><p>{meta.subpattern}</p><div className="complexity-pills"><span>Time {meta.time_complexity_target}</span><span>Space {meta.space_complexity_target}</span></div><p>{meta.educational_utility}</p>{meta.prerequisites.length > 0 && <p><b>Prerequisites:</b> {meta.prerequisites.join(', ')}</p>}</div>}
        <h2>Description</h2>{problem.description ? <p className="description">{problem.description}</p> : <div className="missing-content"><h3>Statement not yet available</h3><p>This entry contains curated teaching metadata. An original problem statement, constraints, signature, and verified tests have not been added. Use the original problem link for the statement.</p></div>}
        {problem.examples.map((example, i) => <div className="example" key={example.id}><h3>Example {i + 1}</h3><label>Input<pre>{example.input_data.trim()}</pre></label><label>Expected output<pre>{example.expected_output.trim()}</pre></label></div>)}
        <h2>Constraints</h2><p className="constraints">{problem.constraints ?? 'Constraints have not been catalogued for this question.'}</p>
        {problem.function_signature && <><h2>Function signature</h2><pre className="signature">{problem.function_signature};</pre><p className="fine-print">Write the function body. Reference drivers supply the C++ includes and any required node types.</p></>}
        {mode === 'guided' && meta.common_misconceptions.length > 0 && <details className="misconceptions"><summary>Common misconceptions</summary><ul>{meta.common_misconceptions.map(text => <li key={text}>{text}</li>)}</ul></details>}
        <div className="problem-footer">{problem.executable ? `${problem.test_count} available verified cases` : 'Verification pending'}<span>Source: {meta.provenance === 'user_repo' ? 'Original solution repository' : 'Curated core'}</span></div>
      </div>
    </article>
    <div className="panel-separator" role="separator" aria-label="Resize problem and editor panels" aria-orientation="vertical" aria-valuemin={28} aria-valuemax={56} aria-valuenow={split} tabIndex={0}
      onKeyDown={e => { if (['ArrowLeft', 'ArrowRight'].includes(e.key)) { e.preventDefault(); setSplit(s => Math.max(28, Math.min(56, s + (e.key === 'ArrowRight' ? 2 : -2)))) } }}
      onPointerDown={e => { e.currentTarget.setPointerCapture(e.pointerId) }}
      onPointerMove={e => { if (e.currentTarget.hasPointerCapture(e.pointerId)) { const bounds = e.currentTarget.parentElement!.getBoundingClientRect(); setSplit(Math.max(28, Math.min(56, ((e.clientX - bounds.left) / bounds.width) * 100))) } }}
      onPointerUp={e => e.currentTarget.releasePointerCapture(e.pointerId)}><span /></div>
    <div className="code-pane">
      <div className="pane-toolbar"><span><Icon name="code" /> Code <span className="quiet-badge">C++14</span></span><span className="saved-label"><Icon name={draft.error ? 'alert' : 'check'} size={13} /> {draft.error ? 'Not saved' : 'Saved locally'}</span></div>
      <div className="editor-controls"><span className="editor-filename">{problem.id}.cpp</span><div><button className="icon-button" onClick={save} aria-label="Save draft" title="Save draft · Ctrl+S"><Icon name="check" /></button><button className="icon-button" onClick={download} aria-label="Download C++ draft" title="Download C++ draft"><Icon name="download" /></button></div></div>
      {draft.error && <p className="error-message" role="alert">{draft.error}</p>}
      <div className="editor-container" style={{ height }}><EditorBoundary fallback={<div className="editor-fallback"><p>Monaco is unavailable. Your draft remains editable below.</p><textarea aria-label="C++ code editor" value={draft.code} onChange={e => changeCode(e.target.value)} /></div>}><Suspense fallback={<div className="editor-loading" role="status">Loading local C++ editor…</div>}><Editor value={draft.code} onChange={changeCode} onSave={save} theme={theme} /></Suspense></EditorBoundary></div>
      <div className="editor-size"><label htmlFor="editor-height">Editor height</label><input id="editor-height" aria-label="Editor height" type="range" min="240" max="720" step="20" value={height} onChange={e => setHeight(Number(e.target.value))} /><span>{height}px</span></div>
      <div className="editor-actions"><span className="fine-print" role="status">{savedNotice || 'Drafts stay on this device · Ctrl+S to save'}</span><div><button className="secondary-button" onClick={() => setResultsOpen(true)}><Icon name="play" size={15} /> View results</button><button className="disabled-run" disabled title="Browser execution is unavailable until isolation is verified"><Icon name="lock" size={14} /> Run pending</button></div></div>
      {!problem.executable && <div className="catalogue-editor-note">No verified signature is available. You can keep notes or a C++ draft here; grounded hints and judging are pending.</div>}
      <Mentor problem={problem} />
      <Review problem={problem} code={draft.code} />
      <Results problem={problem} open={resultsOpen} onToggle={() => setResultsOpen(!resultsOpen)} />
    </div>
  </div>
}
