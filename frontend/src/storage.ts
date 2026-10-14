export function loadDraft(id: string, starter: string): { code: string; error: string | null } {
  try {
    const raw = localStorage.getItem(`mentor:draft:${id}`)
    if (!raw) return { code: starter, error: null }
    const draft: unknown = JSON.parse(raw)
    if (typeof draft === 'object' && draft !== null && 'code' in draft && typeof draft.code === 'string') return { code: draft.code, error: null }
    return { code: starter, error: 'Saved draft is unreadable. It has not been overwritten.' }
  } catch { return { code: starter, error: 'Browser storage is unavailable or the saved draft is unreadable.' } }
}
export function saveDraft(id: string, code: string): string | null {
  try { localStorage.setItem(`mentor:draft:${id}`, JSON.stringify({ code, updatedAt: new Date().toISOString() })); return null }
  catch { return 'Draft could not be saved locally. Download your code to keep a copy.' }
}
export function readPreference(key: string, fallback: string): string {
  try { return localStorage.getItem(`mentor:${key}`) ?? fallback } catch { return fallback }
}
export function writePreference(key: string, value: string) { try { localStorage.setItem(`mentor:${key}`, value) } catch { /* preference is still usable for this page */ } }
export function readSession(id: string): string | null { try { return sessionStorage.getItem(`mentor:session:${id}`) } catch { return null } }
export function saveSession(id: string, value: string) { try { sessionStorage.setItem(`mentor:session:${id}`, value) } catch { /* current in-memory session remains usable */ } }
