import { useEffect, useRef, useState } from 'react'
import { api } from './api'
import type { Mode, Problem, Question, Theme } from './types'
import { readPreference, writePreference } from './storage'
import { filterQuestions, sortQuestions, questionLabel } from './catalogue'
import type { SortOrder } from './catalogue'
import Icon from './Icon'
import Workspace from './Workspace'
import LearnDSA from './LearnDSA'

export default function App() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [problem, setProblem] = useState<Problem | null>(null)
  const [selected, setSelected] = useState('lc_167')
  const [mode, setMode] = useState<Mode>('independent')
  const [theme, setTheme] = useState<Theme>(() => readPreference('theme', 'dark') === 'light' ? 'light' : 'dark')
  const [query, setQuery] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [pattern, setPattern] = useState('')
  const [subpattern, setSubpattern] = useState('')
  const [sort, setSort] = useState<SortOrder>('number')
  const [screen, setScreen] = useState<'practice' | 'learn'>('practice')
  const [lesson, setLesson] = useState('binary-search')
  const [tutorOnline, setTutorOnline] = useState<boolean | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [browserOpen, setBrowserOpen] = useState(false)
  const loadSequence = useRef(0)
  useEffect(() => { document.documentElement.dataset.theme = theme; writePreference('theme', theme) }, [theme])
  useEffect(() => {
    let active = true
    api.bootstrap().then(() => api.questions()).then(async value => {
      if (!active) return
      setQuestions(value)
      const initial = await api.problem('lc_167')
      if (active && loadSequence.current === 0) { setProblem(initial); setLoading(false) }
      api.health().then(health => { if (active) setTutorOnline(health.tutor_available) }).catch(() => { if (active) setTutorOnline(false) })
    }).catch(err => { if (active) { setError(err instanceof Error ? err.message : 'API unavailable. Start the local backend and reload.'); setLoading(false) } })
    return () => { active = false }
  }, [])
  async function selectQuestion(id: string) {
    setScreen('practice')
    const sequence = ++loadSequence.current
    setSelected(id); setProblem(null); setLoading(true); setError(''); setBrowserOpen(false)
    try { const detail = await api.problem(id); if (sequence === loadSequence.current) { setProblem(detail); setLoading(false) } }
    catch (err) { if (sequence === loadSequence.current) { setError(err instanceof Error ? err.message : 'Question could not be loaded.'); setLoading(false) } }
  }
  function changeMode(value: Mode) { setMode(value); setPattern(''); setSubpattern('') }
  const shown = sortQuestions(filterQuestions(questions, query, difficulty, pattern, subpattern, mode), sort)
  const patterns = [...new Set(questions.map(q => q.pattern))].sort()
  const subpatterns = [...new Set(questions.filter(q => !pattern || q.pattern === pattern).map(q => q.subpattern))].sort()
  return <div className="app-shell">
    <a className="skip-link" href="#practice">Skip to practice workspace</a>
    <header className="app-header"><div className="brand"><div className="brand-mark"><Icon name="code" size={24} /></div><div><strong>Coding Mentor<span className="brand-dot">.</span></strong><small>LESS ANSWER. MORE UNDERSTANDING.</small></div></div>
      <div className="header-actions"><nav className="section-switch" aria-label="Learning section"><button aria-pressed={screen === 'practice'} onClick={() => setScreen('practice')}>Practice</button><button aria-pressed={screen === 'learn'} onClick={() => setScreen('learn')}>Learn DSA</button></nav><div className="mode-switch" aria-label="Practice mode"><button className={mode === 'independent' ? 'selected' : ''} aria-pressed={mode === 'independent'} onClick={() => changeMode('independent')}>Independent practice</button><button className={mode === 'guided' ? 'selected' : ''} aria-pressed={mode === 'guided'} onClick={() => changeMode('guided')}>Guided learning</button></div>
        <button className="theme-button icon-button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}><Icon name={theme === 'dark' ? 'sun' : 'moon'} /></button></div>
    </header>
    <div className="workspace-strip"><span>{screen === 'practice' && <button className="browse-toggle icon-button" onClick={() => setBrowserOpen(!browserOpen)} aria-label="Toggle question browser" aria-expanded={browserOpen}><Icon name="menu" /></button>}<span className="eyebrow">YOUR PRACTICE SPACE</span><span className="strip-divider">/</span><span>{screen === 'learn' ? 'Learn DSA · patterns and subpatterns' : problem ? questionLabel(problem.metadata) : 'Choose a problem'}</span></span><span className={`connection ${tutorOnline === true ? 'online' : ''}`}><span className="status-dot" />{tutorOnline === null ? 'Checking local mentor…' : tutorOnline ? 'Local mentor connected' : 'Mentor offline · drafts available'}<button className="icon-button" aria-label="Refresh mentor connection" onClick={() => void api.health().then(value => setTutorOnline(value.tutor_available)).catch(() => setTutorOnline(false))}><Icon name="refresh" size={13} /></button></span></div>
    <div className={`app-body ${screen === 'learn' ? 'learning-body' : ''}`}>
      {screen === 'learn' ? <main id="practice" className="main-workspace" tabIndex={-1}><LearnDSA questions={questions} practice={id => void selectQuestion(id)} selected={lesson} onSelect={setLesson} /></main> : <>
      <aside className={`catalogue-sidebar ${browserOpen ? 'mobile-open' : ''}`} aria-label="Question browser"><div className="catalogue-heading"><div><Icon name="book" /><h2>Question library</h2></div><span>{questions.length}</span></div><p className="catalogue-description">A considered curriculum.<br />One problem at a time.</p>
        <label className="search-box"><Icon name="search" size={16} /><input aria-label="Search questions" placeholder="Number, title, pattern…" value={query} onChange={e => setQuery(e.target.value)} /></label>
        <div className="catalogue-filters"><label>Sort by<select aria-label="Sort questions" value={sort} onChange={e => setSort(e.target.value as SortOrder)}><option value="number">LeetCode number</option><option value="difficulty">Difficulty</option><option value="topic">Topic</option></select></label><label>Difficulty<select value={difficulty} onChange={e => setDifficulty(e.target.value)}><option value="">All difficulties</option>{['Easy', 'Medium', 'Hard'].map(d => <option key={d}>{d}</option>)}</select></label>
          {mode === 'guided' ? <><label>Pattern<select value={pattern} onChange={e => { setPattern(e.target.value); setSubpattern('') }}><option value="">All patterns</option>{patterns.map(p => <option key={p}>{p}</option>)}</select></label><label>Subpattern<select value={subpattern} onChange={e => setSubpattern(e.target.value)}><option value="">All subpatterns</option>{subpatterns.map(s => <option key={s}>{s}</option>)}</select></label></> : <p className="filter-note"><Icon name="lock" size={13} /> Pattern filters are hidden in independent practice.</p>}
        </div>
        <div className="catalogue-count"><span>{shown.length} questions</span><span>{questions.filter(q => q.executable).length} verified suites</span></div>
        <nav className="question-list" aria-label="Questions">{shown.map(q => <button key={q.id} className={`question-card ${selected === q.id ? 'active' : ''}`} onClick={() => void selectQuestion(q.id)} aria-current={selected === q.id ? 'page' : undefined}><span className="question-card-body"><strong>{questionLabel(q)}</strong><span><small className={`difficulty-text ${q.difficulty.toLowerCase()}`}>{q.difficulty}</small><small className={`catalogue-tag ${q.executable ? 'verified' : ''}`}>{q.executable ? 'Verified suite' : 'Catalogue'}</small></span>{mode === 'guided' && <small className="question-pattern">{q.pattern}</small>}</span>{selected === q.id && <span className="selected-dot" />}</button>)}{!loading && shown.length === 0 && <div className="no-questions">No matching questions.<button onClick={() => { setQuery(''); setDifficulty(''); setPattern(''); setSubpattern('') }}>Clear filters</button></div>}</nav>
        <div className="sidebar-footer"><span className="status-dot" /> Local-first learning<span>Drafts stay in this browser.</span></div>
      </aside>
      <main id="practice" className="main-workspace" tabIndex={-1}>{loading ? <div className="workspace-loading" role="status"><Icon name="book" size={30} /><h2>Opening your practice space…</h2><p>Loading the original catalogue and verified problem content.</p></div> : error ? <div className="workspace-loading error-state" role="alert"><Icon name="alert" size={30} /><h2>The local API is unavailable</h2><p>{error}</p><button className="primary-button" onClick={() => questions.length ? void selectQuestion(selected) : window.location.reload()}>Retry connection</button><p className="fine-print">Start the FastAPI server on 127.0.0.1:8000. Saved drafts are kept locally.</p></div> : problem ? <Workspace key={problem.id} problem={problem} theme={theme} mode={mode} /> : null}</main></>}
    </div>
    <footer className="app-footer"><span>Think independently. Ask intentionally.</span><span>Browser execution pending isolation · AI advice is not a verdict</span></footer>
  </div>
}
