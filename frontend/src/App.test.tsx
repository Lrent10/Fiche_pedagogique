// @vitest-environment jsdom

import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useState } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { post, put } from './api'
import { SheetEditor, TeacherPreview } from './App'
import type { SheetDetail } from './types'

vi.mock('./api', () => ({
  api: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
}))

const mockedPut = vi.mocked(put)
const mockedPost = vi.mocked(post)

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
    mockedPut.mockResolvedValueOnce(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '3ème B' } }))
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '3ème B' } })
    fireEvent.click(screen.getByRole('button', { name: /Planification/ }))

    expect(await screen.findByRole('heading', { name: 'Éléments de planification' })).toBeTruthy()
    expect(mockedPut).toHaveBeenCalledTimes(1)
    expect(mockedPut.mock.calls[0][1]).toEqual(expect.objectContaining({
      identification: expect.objectContaining({ classe: '3ème B' }),
    }))
  })

  it('ne lance pas deux sauvegardes lors d’un double clic de navigation', async () => {
    const pending = deferred<SheetDetail>()
    mockedPut.mockReturnValueOnce(pending.promise)
    renderEditor()
    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '3ème B' } })
    const next = screen.getByRole('button', { name: /Suivant/ })

    fireEvent.click(next)
    fireEvent.click(next)
    expect(mockedPut).toHaveBeenCalledTimes(1)

    await act(async () => pending.resolve(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '3ème B' } })))
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
    render(<TeacherPreview sheet={sheet({ identification: { établissement: '', discipline: 'Mathématiques', classe: '3ème B' } })} />)
    expect(screen.getByText('Mathématiques · 3ème B')).toBeTruthy()
    expect(screen.queryByText('Mathématiques · 4e')).toBeNull()
  })

  it('TEST-006 ne rend l’export accessible qu’après persistance des données modifiées', async () => {
    const pending = deferred<SheetDetail>()
    mockedPut.mockReturnValueOnce(pending.promise)
    mockedPost.mockResolvedValueOnce({ download_url: '/exports/fiche.pdf' })
    renderEditor()

    fireEvent.change(screen.getByLabelText('classe'), { target: { value: '3ème B' } })
    fireEvent.click(screen.getByRole('button', { name: /Aperçu & édition finale/ }))
    expect(screen.queryByRole('button', { name: 'Aperçu impression (PDF)' })).toBeNull()

    await act(async () => pending.resolve(sheet({ identification: { établissement: 'CEG Initial', discipline: 'Mathématiques', classe: '3ème B' } })))
    fireEvent.click(await screen.findByRole('button', { name: 'Aperçu impression (PDF)' }))
    await waitFor(() => expect(mockedPost).toHaveBeenCalledWith('/api/exports', expect.objectContaining({ revision_id: 7 })))
    expect(mockedPut.mock.invocationCallOrder[0]).toBeLessThan(mockedPost.mock.invocationCallOrder[0])
  })
})
