import { beforeEach, expect, it, vi } from 'vitest'
import { loadDraft, saveDraft } from './storage'
beforeEach(() => { localStorage.clear(); vi.restoreAllMocks() })
it('keeps blank drafts instead of replacing them with starter code', () => { saveDraft('lc_167', ''); expect(loadDraft('lc_167', 'starter').code).toBe('') })
it('does not overwrite a corrupt stored draft', () => { localStorage.setItem('mentor:draft:lc_167', 'invalid'); expect(loadDraft('lc_167', 'starter').error).not.toBeNull(); expect(localStorage.getItem('mentor:draft:lc_167')).toBe('invalid') })
it('reports quota failures explicitly', () => { vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('quota') }); expect(saveDraft('lc_167', 'code')).toMatch(/could not be saved/) })
