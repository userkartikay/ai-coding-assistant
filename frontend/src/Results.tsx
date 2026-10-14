import { useEffect, useRef, useState } from 'react'
import { api } from './api'
import type { JudgeReport, Problem, ReferenceResults } from './types'
import Icon from './Icon'

export default function Results({ problem, open, onToggle }: { problem: Problem; open: boolean; onToggle: () => void }) {
  const [references, setReferences] = useState<ReferenceResults | null>(null)
  const [mock, setMock] = useState<JudgeReport | null>(null)
  const [source, setSource] = useState('canonical')
  const [scenario, setScenario] = useState('WA')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(problem.executable)
  const requestSequence = useRef(0)
  const currentSource = useRef('canonical')
  useEffect(() => {
    let active = true
    if (problem.executable) api.references(problem.id).then(value => { if (active) { setReferences(value); if (currentSource.current !== 'mock') setLoading(false) } }).catch(err => { if (active && currentSource.current !== 'mock') { setError(err.message); setLoading(false) } })
    return () => { active = false }
  }, [problem.id, problem.executable])
  async function loadMock(nextScenario: string) {
    const sequence = ++requestSequence.current
    setLoading(true); setError(''); setMock(null)
    try { const value = await api.mock(problem.id, nextScenario); if (sequence === requestSequence.current) setMock(value.report) }
    catch (err) { if (sequence === requestSequence.current) setError(err instanceof Error ? err.message : 'Mock preview unavailable.') }
    finally { if (sequence === requestSequence.current) setLoading(false) }
  }
  function changeSource(value: string) {
    ++requestSequence.current; currentSource.current = value; setSource(value); setError('')
    if (value === 'mock') void loadMock(scenario)
    else { setLoading(false); if (!references) setError('Reference reports are unavailable. The mock preview remains available.') }
  }
  const report = source === 'mock' ? mock : references?.reports[source === 'known_bug' ? 'known_bug' : 'canonical']
  return <section className="results panel-section" aria-label="Test results">
    <button className="section-heading" onClick={onToggle} aria-expanded={open}><span><span className="section-icon"><Icon name="play" /></span> Test results <span className="quiet-badge">Reference / mock</span></span><Icon name="chevron" /></button>
    {open && <div className="section-content">
      <div className="notice"><Icon name="lock" /><p><strong>Your draft has not been executed.</strong> Browser execution is pending verified isolation. These reports describe trusted fixtures or a mock display preview.</p></div>
      {!problem.executable ? <p className="muted">This catalogue-only question has no verified test suite yet.</p> : <>
        <div className="results-controls"><label>Report source<select value={source} onChange={e => changeSource(e.target.value)}><option value="canonical">Trusted reference solution</option><option value="known_bug">Trusted known-bug fixture</option><option value="mock">Mock display preview</option></select></label>
          {source === 'mock' && <label>Mock verdict<select value={scenario} onChange={e => { setScenario(e.target.value); void loadMock(e.target.value) }}>{['WA', 'AC', 'COMPILATION_ERROR', 'TLE', 'RUNTIME_ERROR'].map(v => <option key={v}>{v}</option>)}</select></label>}
        </div>
        {source === 'mock' && <div className="mock-label">MOCK PREVIEW · Not a compiler run or a correctness result</div>}
        {loading ? <p role="status">Loading result evidence…</p> : error ? <div role="alert" className="error-message"><Icon name="alert" /><p>{error}</p></div> : report ? <>
          <div className="verdict-row"><strong className={`verdict ${report.overall_verdict === 'AC' ? 'accepted' : 'failed'}`}>{report.overall_verdict}</strong><div><b>{report.passed_tests}/{report.total_tests} available tests passed</b><small>{source === 'mock' ? 'Illustrative data only' : 'Verified trusted fixture · not your draft'}</small></div></div>
          {report.overall_verdict === 'AC' && <p className="fine-print">AC means this fixture passed the available verified suite. It is not proof of correctness for every input.</p>}
          {source !== 'mock' && references && <p className="fine-print">Recorded {new Date(references.recorded_at).toLocaleString()} · compile {report.compilation_time_ms.toFixed(0)} ms</p>}
          {report.compilation_output && <div className="compiler-errors"><h4>Compiler diagnostics</h4><pre>{report.compilation_output}</pre></div>}
          <div className="test-cases">{report.test_results.map(result => <details key={result.test_case_id}><summary><span className={result.passed ? 'mint-text' : 'amber-text'}>{result.passed ? '✓' : '×'}</span><strong>{result.test_case_id}</strong><span className="muted">{result.verdict}</span></summary><div className="case-detail">
            <label>Input<pre>{result.input_data ?? '(empty)'}</pre></label><label>Expected output<pre>{result.expected_output ?? '(unavailable)'}</pre></label><label>{source === 'mock' ? 'Mock output' : 'Actual fixture output'}<pre>{result.actual_output ?? '(none)'}</pre></label>
            {result.error_message && <p className="amber-text">{result.error_message}</p>}{Boolean(result.truncated_fields?.length) && <p className="fine-print">Large fields are shown as labeled excerpts.</p>}
          </div></details>)}</div>
        </> : null}
      </>}
    </div>}
  </section>
}
