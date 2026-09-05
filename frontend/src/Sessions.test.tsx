// @vitest-environment jsdom
import { useState } from 'react'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { api, post, put } from './api'
import { DurationFields, PlannedSessionCreate, SessionPanel, proposedBreak } from './Sessions'
import type { SessionDurations, SheetDetail } from './types'

vi.mock('./api', () => ({ api: vi.fn(), post: vi.fn(), put: vi.fn() }))
const context = { id: 1, class_level: '4e', class_label: '4e A', school_year: '2026-2027', teacher_actual_weekly_minutes: null }
const ins = [{ id: 3, text: 'Instruction A' }, { id: 4, text: 'Instruction B' }]
const catalog = [{ id: 1, level: '4e', situations: [{ id: 1, title: 'SA', sequences: [{ id: 1, title: 'Algèbre', instructions: ins }] }] }]
const plan = { id: 1, next_session_number: 1, sessions: [], planned_sequence_minutes: null }
const rows = ins.map(i => ({ instruction_id: i.id, code: 'INS' + i.id, text: i.text, status: i.id === 3 ? 'PARTIAL' : 'SKIPPED', eligible: true, actual_minutes: 0, previously_skipped: i.id === 4, planned_in_sessions: [2] }))
const sheet: SheetDetail = { id: 7, sheet_id: 5, title: 'Séance', code: 'F', status: 'FINALIZED', revision_number: 1, identification: { classe: '4e A' }, planning: {}, resources: [], flow: [], support_use: null, planned_session: { id: 1, number: 1, sequence_plan_id: 1 }, segments: ins.map(i => ({ id: i.id, instruction_id: i.id, instruction_code: 'INS' + i.id, text: i.text, planned_minutes: 0 })), authoring: { session_preparation: { durations: { slot_minutes: 120, break_minutes: 10, default_break_minutes: 10, break_override: false, pedagogical_minutes: 110 }, class_context_id: 1, class_label: '4e A', school_year: '2026-2027', session_number: 1, teacher_actual_weekly_minutes: null, planned_sequence_minutes: null, deferred_instruction_ids: [], reactivate_instruction_ids: [] } } }
beforeEach(() => { vi.resetAllMocks(); localStorage.clear(); vi.mocked(api).mockImplementation(async path => path.endsWith('/contexts') ? [context] : path === '/api/authoring/curriculum' ? catalog : path.includes('/coverage?') ? { instructions: rows } : path.includes('recommendation') ? rows : plan); vi.mocked(post).mockResolvedValue(plan); vi.mocked(put).mockResolvedValue(sheet); HTMLDialogElement.prototype.showModal = function () { this.open = true } })
afterEach(cleanup)

it('T10 seuils 119/120/130, profil et surcharge locale', () => {
  expect([119, 120, 130].map(s => proposedBreak(s, 10))).toEqual([0, 10, 10])
  function Form() { const [d, setD] = useState<SessionDurations>({ slot_minutes: 120, break_minutes: 10, default_break_minutes: 10, break_override: false }); return <DurationFields value={d} onChange={setD} /> }
  render(<Form />)
  fireEvent.change(screen.getByLabelText('Créneau brut (min)'), { target: { value: '119' } })
  expect((screen.getByLabelText('Pause (min)') as HTMLInputElement).value).toBe('0')
  fireEvent.change(screen.getByLabelText('Pause (min)'), { target: { value: '5' } })
  fireEvent.change(screen.getByLabelText('Pause habituelle dès 120 min'), { target: { value: '15' } })
  expect((screen.getByLabelText('Pause (min)') as HTMLInputElement).value).toBe('5')
})

it('T02 double clic ne crée qu’une demande, numéro explicite', async () => {
  render(<PlannedSessionCreate onCreated={vi.fn()} onOpen={vi.fn()} />)
  await screen.findByText('Instruction A')
  fireEvent.click(screen.getByText('Voir les séances planifiées'))
  await screen.findByText('Prochaine séance :')
  vi.mocked(post).mockImplementation(() => new Promise(() => {}))
  const button = screen.getByText('Créer la prochaine séance planifiée')
  fireEvent.click(button); fireEvent.click(button)
  expect(vi.mocked(post).mock.calls.filter(([path]) => path.endsWith('/sessions'))).toHaveLength(1)
  expect(post).toHaveBeenLastCalledWith('/api/session-planning/plans/1/sessions', expect.objectContaining({ expected_session_number: 1, instruction_ids: [3, 4] }))
})

it('T07 T08 T22 recommandation séparée et report visible', async () => {
  render(<PlannedSessionCreate onCreated={vi.fn()} onOpen={vi.fn()} />)
  await screen.findByText('Instruction A')
  fireEvent.click(screen.getByText('Voir les séances planifiées'))
  await screen.findByText('Prochaine séance :')
  vi.mocked(post).mockClear()
  fireEvent.click(screen.getByText('Demander une recommandation selon les résultats réels'))
  await screen.findByText('Précédemment sautée')
  expect(screen.getAllByText(/Déjà prévue dans les séances 2/)).toHaveLength(2)
  expect(post).not.toHaveBeenCalled()
  fireEvent.click(screen.getAllByLabelText('Reporter pour cette préparation seulement')[1])
  fireEvent.click(screen.getByText('Utiliser cette proposition dans la préparation courante'))
  expect((screen.getByLabelText('Instruction B') as HTMLInputElement).checked).toBe(false)
})

it('T09 saisie par instruction sans répartition implicite', async () => {
  render(<SessionPanel sheet={sheet} onChange={vi.fn()} />)
  fireEvent.change(screen.getAllByLabelText('Résultat réel')[0], { target: { value: 'PARTIAL' } })
  fireEvent.change(screen.getAllByLabelText('Minutes réellement consacrées')[0], { target: { value: '17' } })
  expect(screen.getByText('1 instruction(s) sans résultat : aucun événement ne sera créé pour elles.')).toBeTruthy()
  fireEvent.click(screen.getByText('Confirmer les résultats saisis'))
  await waitFor(() => expect(post).toHaveBeenCalledWith('/api/session-planning/sessions/1/executions', expect.objectContaining({ results: [{ segment_id: 3, status: 'PARTIAL', actual_minutes: 17 }] })))
})

it('T12 affiche le snapshot malgré un nouveau profil navigateur', () => {
  localStorage.setItem('fichemaths.break', '25')
  render(<SessionPanel sheet={sheet} onChange={vi.fn()} />)
  expect(screen.getByText(/Créneau 120 min · pause 10 min · durée pédagogique 110 min/)).toBeTruthy()
})

it('T15 une erreur de sauvegarde conserve la fenêtre de préparation', async () => {
  vi.mocked(put).mockRejectedValue(new Error('Échec de sauvegarde'))
  render(<SessionPanel sheet={{ ...sheet, status: 'DRAFT' }} onChange={vi.fn()} />)
  fireEvent.click(screen.getByText('Adapter les instructions et les durées de ce brouillon'))
  await screen.findByText('Adapter cette préparation')
  fireEvent.click(screen.getByText('Enregistrer avant de revenir à la fiche'))
  await screen.findByRole('alert')
  expect(screen.getByRole('dialog')).toBeTruthy()
})

it('T15 une erreur des métadonnées empêche de quitter leur saisie', async () => {
  render(<SessionPanel sheet={{ ...sheet, status: 'DRAFT' }} onChange={vi.fn()} beforeEdit={() => Promise.reject(new Error('Métadonnées non sauvegardées'))} />)
  fireEvent.click(screen.getByText('Adapter les instructions et les durées de ce brouillon'))
  await screen.findByText('Error: Métadonnées non sauvegardées')
  expect(screen.queryByRole('dialog')).toBeNull()
})


it('T07 les instructions couvertes sont exclues dès la préparation initiale', async () => {
  vi.mocked(api).mockImplementation(async path => path.endsWith('/contexts') ? [context] : path === '/api/authoring/curriculum' ? catalog : path.includes('/coverage?') ? { instructions: rows.map(r => ({ ...r, status: r.instruction_id === 3 ? 'COVERED' : 'PARTIAL' })) } : plan)
  render(<PlannedSessionCreate onCreated={vi.fn()} onOpen={vi.fn()} />)
  await screen.findByText('Instruction A')
  await waitFor(() => expect((screen.getByLabelText('Instruction B') as HTMLInputElement).checked).toBe(true))
  expect((screen.getByLabelText('Instruction A') as HTMLInputElement).checked).toBe(false)
})
