// @vitest-environment jsdom

import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useState } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { api, post, put } from './api'
import App, { classLabelMatchesCurriculum, SheetEditor, TeacherPreview } from './App'
import type { SheetDetail } from './types'

vi.mock('./api', () => ({
  api: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
}))

const mockedApi = vi.mocked(api)
const mockedPut = vi.mocked(put)
const mockedPost = vi.mocked(post)
const CLASS_LEVEL_ERROR = 'Cette fiche utilise le programme de 4e. La classe doit appartenir au niveau 4e.'

function sheet(overrides: Partial<SheetDetail> = {}): SheetDetail {
  return {
    id: 7,
    sheet_id: 3,
    code: 'FICHE-TEST',
    title: 'Séance de test',
    revision_number: 1,
    status: 'DRAFT',
    identification: {
      établissement: 'CEG Initial',
      discipline: 'Mathématiques',
      classe: '4e',
    },
    planning: { durée: '55 min' },
    segments: [],
    resources: [],
    flow: [],
    support_use: null,
    ...overrides,
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}

function renderEditor(initial = sheet()) {
  const updates: SheetDetail[] = []
  function Harness() {
    const [current, setCurrent] = useState(initial)
    return <SheetEditor
      sheet={current}
      setSheet={next => { updates.push(next); setCurrent(next) }}
      instructions={[]}
      resources={[]}
      notify={vi.fn()}
      refresh={async () => undefined}
      close={vi.fn()}
    />
  }
  render(<Harness />)
  return { updates }
}

const instructions = [1, 2, 3, 4].map(id => ({
  id,
  code: `SEQ8-INS${id}`,
  text: `Instruction ${id}`,
  position: id,
  sequence_id: 1,
}))
const existingSheet = { sheet_id: 3, revision_id: 7, code: 'FICHE-TEST', title: 'Fiche existante', revision_number: 1, status: 'DRAFT' }

function mockWorkspace() {
  mockedPost.mockImplementation(async (path: string) => {
    if (path === '/api/authoring/preview') return { identification: { classe: '4e' }, planning: {}, instructions, provenance: {}, durations: [], duration_conflict: false }
    if (path === '/api/authoring/compose') return sheet({ title: 'Nouvelle séance' })
    throw new Error(`Requête inattendue: ${path}`)
  })
  mockedApi.mockImplementation(async (path: string) => {
    if (path === '/api/authoring/curriculum') return [{ id: 1, level: '4e', title: 'Programme', situations: [{ id: 1, title: 'SA1', sequences: [{ id: 1, title: 'Séquence', instructions }] }] }]
    if (path === '/api/dashboard') return { draft_sheets: 1, finalized_sheets: 0, resources: 0, supports: 0, open_source_issues: 0 }
    if (path === '/api/instructions') return instructions
    if (path === '/api/resources') return []
    if (path === '/api/sheets') return [existingSheet]
    if (path === '/api/supports') return []
    if (path === '/api/sheets/7') return sheet({ title: 'Fiche existante' })
    throw new Error(`Requête inattendue: ${path}`)
  })
}

describe('UX-BB-002 intention explicite de création', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockWorkspace()
  })

  afterEach(cleanup)

  it('TEST-001 ouvre immédiatement le formulaire depuis le CTA accueil', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /Créer une fiche pédagogique/ }))

    expect(await screen.findByRole('heading', { name: 'Mes fiches enseignant' })).toBeTruthy()
    expect(screen.getByLabelText(/Titre de la séance/i)).toBeTruthy()
  })

  it('TEST-002 ne crée aucune fiche avant la soumission', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /Créer une fiche pédagogique/ }))

    expect(await screen.findByLabelText(/Titre de la séance/i)).toBeTruthy()
    expect(mockedPost.mock.calls.filter(([path]) => path === '/api/authoring/compose')).toHaveLength(0)
  })

  it('TEST-003 soumet une seule fois puis affiche SheetEditor', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /Créer une fiche pédagogique/ }))
    fireEvent.change(await screen.findByLabelText(/Titre de la séance/i), { target: { value: 'Nouvelle séance' } })
    fireEvent.click(await screen.findByRole('button', { name: /Commencer la conception/ }))

    await waitFor(() => expect(mockedPost.mock.calls.filter(([path]) => path === '/api/authoring/compose')).toHaveLength(1))
    expect(mockedPost).toHaveBeenCalledWith('/api/authoring/compose', expect.objectContaining({ title: 'Nouvelle séance' }))
    expect(await screen.findByRole('heading', { name: 'Nouvelle séance' })).toBeTruthy()
  })

  it('TEST-004 garde le formulaire fermé lors de la navigation normale vers Mes fiches', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: '▤ Mes fiches' }))

    expect(await screen.findByRole('heading', { name: 'Mes fiches enseignant' })).toBeTruthy()
    expect(screen.queryByLabelText(/Titre de la séance/i)).toBeNull()
  })

  it('TEST-005 quitte une fiche active et ouvre le formulaire via Nouvelle fiche', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /Fiche existante/ }))
    expect(await screen.findByRole('heading', { name: 'Fiche existante' })).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: '＋ Nouvelle fiche' }))
    expect(await screen.findByLabelText(/Titre de la séance/i)).toBeTruthy()
    expect(screen.queryByRole('button', { name: '← Retour à mes fiches' })).toBeNull()
  })

  it('TEST-006 conserve le formulaire ouvert si l’intention de création est répétée', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /Créer une fiche pédagogique/ }))
    expect(await screen.findByLabelText(/Titre de la séance/i)).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: '＋ Nouvelle fiche' }))
    expect(await screen.findByLabelText(/Titre de la séance/i)).toBeTruthy()
    expect(mockedPost.mock.calls.filter(([path]) => path === '/api/authoring/compose')).toHaveLength(0)
  })

  it('TEST-007 conserve la reprise d’une fiche depuis la liste', async () => {
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: '▤ Mes fiches' }))
    fireEvent.click(await screen.findByRole('button', { name: /Fiche existante/ }))

    expect(await screen.findByRole('heading', { name: 'Fiche existante' })).toBeTruthy()
    expect(screen.getByRole('button', { name: '← Retour à mes fiches' })).toBeTruthy()
  })
})

describe('P2 compétences et sauvegarde avant navigation', () => {
  const selected = { competency_id: 1, context_id: 10, label: 'Travailler en coopération', competency_type: 'TRANSVERSAL', source_document: 'Guide 4e', source_page: '74', authority_class: 'OFFICIAL_GUIDE', selection_origin: 'AUTO_SELECTED' }
  beforeEach(() => { vi.clearAllMocks(); mockedApi.mockResolvedValue([selected]) })
  afterEach(cleanup)

  it('P2-T09 retire et sauvegarde avant Suivant, bloque le double clic', async () => {
    const initial = sheet({ competency_selection: [selected] })
    renderEditor(initial)
    fireEvent.click(screen.getByRole('button', { name: /6 Planification/ }))
    expect(await screen.findByText(/Suggestion automatique/)).toBeTruthy()
    fireEvent.click(screen.getByRole('checkbox'))
    const pending = deferred<SheetDetail>()
    mockedPut.mockReturnValue(pending.promise)
    fireEvent.click(screen.getByRole('button', { name: 'Suivant →' }))
    fireEvent.click(screen.getByRole('button', { name: 'Suivant →' }))
    expect(mockedPut).toHaveBeenCalledTimes(1)
    expect(mockedPut).toHaveBeenCalledWith('/api/competencies/sheets/7', { selections: [] })
    expect(screen.getByText('Compétences proposées pour cette séance')).toBeTruthy()
    await act(async () => pending.resolve({ ...initial, competency_selection: [] }))
    expect(await screen.findByText('Aperçu & édition finale', { selector: 'h3' })).toBeTruthy()
  })

  it('P2-T09 reste sur Planification après échec et permet la reprise', async () => {
    renderEditor(sheet({ competency_selection: [selected] }))
    fireEvent.click(screen.getByRole('button', { name: /6 Planification/ }))
    await screen.findByText(/Suggestion automatique/)
    fireEvent.click(screen.getByRole('checkbox'))
    mockedPut.mockRejectedValue(new Error('Sauvegarde indisponible'))
    fireEvent.click(screen.getByRole('button', { name: 'Suivant →' }))
    expect((await screen.findByRole('alert')).textContent).toContain('Sauvegarde indisponible')
    expect(screen.getByText('Compétences proposées pour cette séance')).toBeTruthy()
  })

  it('P2-T12/T13 ajoute plusieurs CTD et accepte une sélection vide', async () => {
    const rows = [1, 2].map(id => ({ ...selected, competency_id: id, context_id: id, label: `Compétence ${id}`, competency_type: 'TRANSDISCIPLINARY' }))
    mockedApi.mockResolvedValue(rows)
    renderEditor(sheet({ competency_selection: [] }))
    fireEvent.click(screen.getByRole('button', { name: /6 Planification/ }))
    await screen.findByText('Compétence 1')
    fireEvent.click(screen.getByLabelText(/Compétence 1/))
    fireEvent.click(screen.getByLabelText(/Compétence 2/))
    expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(2)
  })
})

describe('DEF-P3-01 état persistant de sélection', () => {
  afterEach(cleanup)

  it('affiche clairement qu’une activité est déjà sélectionnée', () => {
    const resource = { id: 42, code: 'RES-42', title: 'Activité retenue', resource_type: 'ACTIVITY', provenance_kind: 'SOURCED', summary: 'Résumé', estimated_minutes: 10, blocks: [], mappings: [{ instruction_id: 1, instruction_code: 'INS-1', text: 'Instruction', validation_status: 'CURATED' }], sources: [] }
    render(<SheetEditor sheet={sheet({ segments: [{ id: 1, instruction_id: 1, instruction_code: 'INS-1', text: 'Instruction', planned_minutes: 20 }], resources: [{ id: 9, origin: 'LIBRARY_DERIVED', source_resource_version_id: 42, title: 'Activité retenue', adaptation_note: '', position: 1, blocks: [] }] })} setSheet={vi.fn()} instructions={[]} resources={[resource]} notify={vi.fn()} refresh={async () => undefined} close={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: /3 Choix des activités/ }))
    expect(screen.getByRole('button', { name: '✓ Activité sélectionnée' }).hasAttribute('disabled')).toBe(true)
  })
})

describe('contrat de persistance du wizard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'open').mockImplementation(() => null)
    vi.spyOn(window, 'confirm').mockImplementation(() => true)
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('TEST-001 sauvegarde Identification avant de naviguer avec Suivant', async () => {
    const pending = deferred<SheetDetail>()
    const updated = sheet({ identification: { établissement: 'CEG Modifié', discipline: 'Mathématiques', classe: '4e' } })
    mockedPut.mockReturnValueOnce(pending.promise)
    const { updates } = renderEditor()

    fireEvent.change(screen.getByLabelText('établissement'), { target: { value: 'CEG Modifié' } })
    fireEvent.click(screen.getByRole('button', { name: /Suivant/ }))

    expect(mockedPut).toHaveBeenCalledWith('/api/sheets/7/metadata', expect.objectContaining({
      identification: expect.objectContaining({ établissement: 'CEG Modifié' }),
    }))
    expect(screen.getByRole('heading', { name: 'Éléments d’identification' })).toBeTruthy()

    await act(async () => pending.resolve(updated))
    expect(await screen.findByRole('heading', { name: 'Ancrage au programme et au guide' })).toBeTruthy()
    expect(updates.at(-1)?.identification.établissement).toBe('CEG Modifié')
  })

  it('TEST-002 reste sur Identification et affiche une erreur si la sauvegarde échoue', async () => {
    mockedPut.mockRejectedValueOnce(new Error('Serveur indisponible'))
    renderEditor()

    fireEvent.change(screen.getByLabelText('établissement'), { target: { value: 'CEG Modifié' } })
    fireEvent.click(screen.getByRole('button', { name: /Suivant/ }))

    expect((await screen.findByRole('alert')).textContent).toContain('Serveur indisponible')
    expect(screen.getByRole('heading', { name: 'Éléments d’identification' })).toBeTruthy()
  })

  it('TEST-003 navigue sans appel réseau quand aucune métadonnée n’est modifiée', async () => {
    renderEditor()
    fireEvent.click(screen.getByRole('button', { name: /Suivant/ }))

    expect(await screen.findByRole('heading', { name: 'Ancrage au programme et au guide' })).toBeTruthy()
    expect(mockedPut).not.toHaveBeenCalled()
  })

  it('TEST-004 sauvegarde Identification avant une navigation directe du stepper', async () => {
    mockedPut.mockResolvedValueOnce(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '4ème B' } }))
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '4ème B' } })
    fireEvent.click(screen.getByRole('button', { name: /Planification/ }))

    expect(await screen.findByRole('heading', { name: 'Éléments de planification' })).toBeTruthy()
    expect(mockedPut).toHaveBeenCalledTimes(1)
    expect(mockedPut.mock.calls[0][1]).toEqual(expect.objectContaining({
      identification: expect.objectContaining({ classe: '4ème B' }),
    }))
  })

  it('ne lance pas deux sauvegardes lors d’un double clic de navigation', async () => {
    const pending = deferred<SheetDetail>()
    mockedPut.mockReturnValueOnce(pending.promise)
    renderEditor()
    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '4e M1' } })
    const next = screen.getByRole('button', { name: /Suivant/ })

    fireEvent.click(next)
    fireEvent.click(next)
    expect(mockedPut).toHaveBeenCalledTimes(1)

    await act(async () => pending.resolve(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '4e M1' } })))
    expect(await screen.findByRole('heading', { name: 'Ancrage au programme et au guide' })).toBeTruthy()
  })

  it('sauvegarde aussi Planification avant Suivant', async () => {
    mockedPut.mockResolvedValueOnce(sheet({ planning: { durée: '60 min' } }))
    renderEditor()
    fireEvent.click(screen.getByRole('button', { name: /Planification/ }))
    fireEvent.change(screen.getByLabelText('durée'), { target: { value: '60 min' } })
    fireEvent.click(screen.getByRole('button', { name: /Suivant/ }))

    expect(await screen.findByRole('heading', { name: 'Aperçu & édition finale' })).toBeTruthy()
    expect(mockedPut.mock.calls[0][1]).toEqual(expect.objectContaining({ planning: { durée: '60 min' } }))
  })

  it('sauvegarde Planification avant Précédent', async () => {
    mockedPut.mockResolvedValueOnce(sheet({ planning: { durée: '50 min' } }))
    renderEditor()
    fireEvent.click(screen.getByRole('button', { name: /Planification/ }))
    fireEvent.change(screen.getByLabelText('durée'), { target: { value: '50 min' } })
    fireEvent.click(screen.getByRole('button', { name: /Précédent/ }))

    expect(await screen.findByRole('heading', { name: 'Organiser le déroulement' })).toBeTruthy()
    expect(mockedPut).toHaveBeenCalledTimes(1)
  })

  it('TEST-005 construit l’en-tête depuis la discipline et la classe de la révision', () => {
    render(<TeacherPreview sheet={sheet({ identification: { établissement: '', discipline: 'Mathématiques', classe: '4e M1' } })} />)
    expect(screen.getByText('Mathématiques · 4e M1')).toBeTruthy()
    expect(screen.queryByText('Mathématiques · 4e')).toBeNull()
  })

  it('TEST-006 ne rend l’export accessible qu’après persistance des données modifiées', async () => {
    const pending = deferred<SheetDetail>()
    mockedPut.mockReturnValueOnce(pending.promise)
    mockedPost.mockResolvedValueOnce({ download_url: '/exports/fiche.pdf' })
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '4e M1' } })
    fireEvent.click(screen.getByRole('button', { name: /Aperçu & édition finale/ }))
    expect(screen.queryByRole('button', { name: 'Aperçu impression (PDF)' })).toBeNull()

    await act(async () => pending.resolve(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '4e M1' } })))
    fireEvent.click(await screen.findByRole('button', { name: 'Aperçu impression (PDF)' }))
    await waitFor(() => expect(mockedPost).toHaveBeenCalledWith('/api/exports', expect.objectContaining({ revision_id: 7 })))
    expect(mockedPut.mock.invocationCallOrder[0]).toBeLessThan(mockedPost.mock.invocationCallOrder[0])
  })

  it.each(['4e', '4E', '4ème', '4eme', '4e A', '4e M1', '4ème B'])(
    'accepte la classe 4e compatible « %s »',
    classLabel => expect(classLabelMatchesCurriculum(classLabel)).toBe(true),
  )

  it('refuse 3ème M1 avant sauvegarde et conserve l’étape Identification', async () => {
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '3ème M1' } })
    expect(screen.getByRole('alert').textContent).toBe(CLASS_LEVEL_ERROR)
    fireEvent.click(screen.getByRole('button', { name: /Suivant/ }))

    expect(screen.getByRole('heading', { name: 'Éléments d’identification' })).toBeTruthy()
    expect(mockedPut).not.toHaveBeenCalled()
  })

  it('refuse aussi Enregistrer tant que la classe est incompatible', () => {
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '3ème M1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(screen.getByRole('alert').textContent).toBe(CLASS_LEVEL_ERROR)
    expect(mockedPut).not.toHaveBeenCalled()
  })
})


it('T19 finalisation contextualisée exige une confirmation explicite', async () => {
  mockedApi.mockResolvedValue([])
  HTMLDialogElement.prototype.showModal = function () { this.open = true }
  const initial = sheet({ planned_session: { id: 1, number: 1, sequence_plan_id: 1 } })
  mockedPost.mockResolvedValueOnce({ ...initial, status: 'FINALIZED' })
  renderEditor(initial)
  fireEvent.click(screen.getByRole('button', { name: '8 Finalisation' }))
  fireEvent.click(screen.getByRole('button', { name: 'Finaliser la révision' }))
  expect(mockedPost).not.toHaveBeenCalled()
  expect(screen.getByRole('dialog')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer la finalisation' }))
  await waitFor(() => expect(mockedPost).toHaveBeenCalledWith('/api/sheets/7/finalize'))
  expect(screen.queryByRole('dialog')).toBeNull()
})
