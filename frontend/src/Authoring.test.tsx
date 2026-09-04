// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { AuthoringCreate, InstructionChoices, SourceLabel, LearnerFromSheet } from './Authoring'
import { api, post, put } from './api'
import type { SheetDetail } from './types'

vi.mock('./api', () => ({ api: vi.fn(), post: vi.fn(), put: vi.fn() }))
const ins = [{ id: 3, code: 'INS3', text: 'Énoncer les propriétés' }]
const catalog = [{ id: 1, level: '4e', title: 'Programme', situations: [{ id: 1, title: 'SA1', sequences: [{ id: 1, title: 'Algèbre', instructions: ins }] }, { id: 2, title: 'SA2 de test', sequences: [{ id: 2, title: 'Géométrie de test', instructions: [{ id: 9, code: 'INS9', text: 'Autre instruction' }] }] }] }]
const preview = { identification: { classe: '4e', 'titre SA': 'Configurations du plan' }, planning: { 'compétences disciplinaires': 'Résoudre un problème' }, instructions: ins, provenance: {}, durations: [], duration_conflict: false }
const source = { source_kind: 'TEACHER_COMMUNITY', source_ref: 'Fiche enseignante', source_version: 'v1' }
const rows = [1, 2].map(id => ({ id, title: 'Candidat ' + id, provenance: source, blocks: [{ id, title: 'Propriété', block_type: 'PROPERTY', content_latex: '$a=b$' }] }))
const sheet: SheetDetail = { id: 5, sheet_id: 5, code: 'TEST', title: 'Séance', revision_number: 1, status: 'DRAFT', curriculum_level: '4e', identification: { classe: '4e' }, planning: {}, segments: [{ id: 1, instruction_id: 3, instruction_code: 'INS3', text: ins[0].text, planned_minutes: 0 }], resources: [], flow: [], support_use: null, authoring: { scope: { programme_id: 1, scope: 'SEQUENCE', scope_id: 1 }, selections: {} } }

beforeEach(() => {
  vi.resetAllMocks(); localStorage.clear()
  vi.mocked(api).mockImplementation(async path => path === '/api/authoring/curriculum' ? catalog : rows)
  vi.mocked(post).mockImplementation(async path => path === '/api/authoring/preview' ? preview : sheet)
  vi.mocked(put).mockResolvedValue(sheet)
})
afterEach(cleanup)

it('UX-001 expose les quatre périmètres', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  await screen.findByText('I. Identification issue du curriculum')
  expect((screen.getByLabelText('Périmètre') as HTMLSelectElement).options).toHaveLength(4)
})
it('UX-002 filtre les séquences lors du changement de SA', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  await screen.findByText('I. Identification issue du curriculum')
  fireEvent.change(screen.getByLabelText('Situation d’apprentissage'), { target: { value: '2' } })
  expect(screen.queryByRole('option', { name: 'Algèbre' })).toBeNull()
  expect(screen.getByRole('option', { name: 'Géométrie de test' })).toBeTruthy()
  await waitFor(() => expect(post).toHaveBeenCalledWith('/api/authoring/preview', { programme_id: 1, scope: 'SEQUENCE', scope_id: 2 }))
})
it('UX-003 affiche les instructions du périmètre', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  expect(await screen.findByText('Énoncer les propriétés')).toBeTruthy()
})
it('UX-004 préremplit I sans saisie', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  expect(await screen.findByText('Configurations du plan')).toBeTruthy()
  expect(screen.queryByRole('textbox', { name: 'titre SA' })).toBeNull()
})
it('UX-005 préremplit II sans saisie', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  expect(await screen.findByText('Résoudre un problème')).toBeTruthy()
})
it('UX-006 affiche plusieurs candidats', async () => {
  render(<InstructionChoices sheet={sheet} onChange={vi.fn()} />)
  expect(await screen.findByText('Candidat 1')).toBeTruthy()
  expect(screen.getByText('Candidat 2')).toBeTruthy()
})
it('UX-007 distingue la source communautaire de la source officielle', () => {
  render(<SourceLabel source={source} />)
  expect(screen.getByText('Communauté enseignante')).toBeTruthy()
  expect(screen.queryByText('Guide officiel')).toBeNull()
  expect(screen.getByText(/Version : v1/)).toBeTruthy()
})
it('UX-008 remplace une sélection et transmet le brouillon sauvegardé', async () => {
  const changed = vi.fn()
  render(<InstructionChoices sheet={sheet} onChange={changed} />)
  await screen.findByText('Candidat 1')
  fireEvent.click(screen.getAllByText('Choisir cette ressource')[1])
  await waitFor(() => expect(changed).toHaveBeenCalledWith(sheet))
  expect(put).toHaveBeenCalledWith('/api/authoring/sheets/5/selection', { instruction_id: 3, resource_version_id: 2 })
})
it('UX-009 montre les formulations comme propriétés', async () => {
  render(<InstructionChoices sheet={sheet} onChange={vi.fn()} />)
  await screen.findByText('Candidat 1')
  expect(screen.getAllByText('Propriété').filter(node => node.tagName === 'SMALL')).toHaveLength(2)
})
it('UX-010_011_012 composition automatique renvoie un brouillon sans finaliser', async () => {
  const created = vi.fn()
  render(<AuthoringCreate onCreated={created} />)
  fireEvent.click(await screen.findByText('Composition automatique'))
  await waitFor(() => expect(created).toHaveBeenCalledWith(sheet))
  expect(post).toHaveBeenCalledWith('/api/authoring/compose', expect.objectContaining({ automatic: true }))
  expect(vi.mocked(post).mock.calls.some(([p]) => p.includes('/finalize'))).toBe(false)
})
it('UX-013 précise le rôle du support sans proposer de zone de réponse', () => {
  render(<LearnerFromSheet sheet={sheet} />)
  expect(screen.getByText(/sans résultats attendus ni zones de réponse/)).toBeTruthy()
  expect(screen.queryByRole('textbox')).toBeNull()
})
it('UX-014 identifie un résultat attendu comme enseignant', async () => {
  vi.mocked(api).mockResolvedValue([{ ...rows[0], blocks: [{ id: 1, title: 'Réponse', block_type: 'EXPECTED_RESPONSE', content_latex: 'Réservé au professeur' }] }])
  render(<InstructionChoices sheet={sheet} onChange={vi.fn()} />)
  expect(await screen.findByText('Résultat attendu — enseignant')).toBeTruthy()
})
it('UX-016 désactive la sélection après finalisation', async () => {
  render(<InstructionChoices sheet={{ ...sheet, status: 'FINALIZED' }} onChange={vi.fn()} />)
  await screen.findByText('Candidat 1')
  expect(screen.getAllByText('Choisir cette ressource').every(button => (button as HTMLButtonElement).disabled)).toBe(true)
  expect(screen.queryByText('Enregistrer dans ma bibliothèque')).toBeNull()
})
it('ne crée pas de fiche géante au périmètre classe', async () => {
  render(<AuthoringCreate onCreated={vi.fn()} />)
  await screen.findByText('Composition automatique')
  fireEvent.change(screen.getByLabelText('Périmètre'), { target: { value: 'CLASS' } })
  expect(await screen.findByText(/Choisissez une SA ou une séquence pour créer/)).toBeTruthy()
  expect(screen.queryByText('Composition automatique')).toBeNull()
})
