import { useEffect, useRef } from 'react'
import * as monaco from 'monaco-editor/editor/editor.api.js'
import { language, conf } from 'monaco-editor/languages/definitions/cpp/cpp.js'
import EditorWorker from 'monaco-editor/editor/editor.worker.js?worker'
import type { Theme } from './types'

;(self as typeof self & { MonacoEnvironment?: monaco.Environment }).MonacoEnvironment = { getWorker: () => new EditorWorker() }
monaco.languages.register({ id: 'cpp', extensions: ['.cpp', '.h'], aliases: ['C++'] })
monaco.languages.setMonarchTokensProvider('cpp', language)
monaco.languages.setLanguageConfiguration('cpp', conf)

export default function CodeEditor({ value, onChange, onSave, theme }: { value: string; onChange: (value: string) => void; onSave: () => void; theme: Theme }) {
  const container = useRef<HTMLDivElement>(null)
  const instance = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const callbacks = useRef({ onChange, onSave })
  useEffect(() => { callbacks.current = { onChange, onSave } }, [onChange, onSave])
  useEffect(() => {
    if (!container.current) return
    const editor = monaco.editor.create(container.current, {
      value, language: 'cpp', theme: theme === 'dark' ? 'vs-dark' : 'vs',
      automaticLayout: true, minimap: { enabled: false }, fontSize: 14,
      fontFamily: "'Cascadia Code', Consolas, monospace", lineHeight: 24,
      padding: { top: 18, bottom: 18 }, tabSize: 4, scrollBeyondLastLine: false,
      wordWrap: 'on', accessibilitySupport: 'on', ariaLabel: 'C++ code editor',
      renderLineHighlight: 'gutter', fixedOverflowWidgets: true,
    })
    instance.current = editor
    const subscription = editor.onDidChangeModelContent(() => callbacks.current.onChange(editor.getValue()))
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => callbacks.current.onSave())
    return () => { subscription.dispose(); editor.getModel()?.dispose(); editor.dispose(); instance.current = null }
    // Each workspace is keyed by problem ID; initial code/theme is synchronized below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  useEffect(() => { if (instance.current && instance.current.getValue() !== value) instance.current.setValue(value) }, [value])
  useEffect(() => { monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs') }, [theme])
  return <div className="monaco-host" ref={container} />
}
