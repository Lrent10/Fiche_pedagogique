import { useEffect, useState } from 'react'
import { api, post, put } from './api'
import type { SheetDetail } from './types'
import { LatexPreview } from './LatexPreview'

type Resource = { id: number; resource_version_id: number; resource_type: string; title: string; content: string; origin_type: string; validation_status: string }
type Document = { origin: string; display_label: string; author?: string; title?: string; edition?: string; note?: string }

export function SessionResources({ sheet, onChange }: { sheet: SheetDetail; onChange: (value: SheetDetail) => void }) {
  const instruction = sheet.segments[0]
  const [items, setItems] = useState<Resource[]>([])
  const [form, setForm] = useState(false)
  const [text, setText] = useState('')
  const [visibility, setVisibility] = useState('PRIVATE')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const load = async () => { if (instruction) { const rows = await api<unknown>(`/api/pedagogical-resources/by-instruction/${instruction.instruction_id}`); setItems(Array.isArray(rows) ? rows.filter(row => row && typeof row === 'object' && 'resource_version_id' in row) as Resource[] : []) } }
  useEffect(() => { void load() }, [instruction?.instruction_id])
  const selected = sheet.resources.map(row => row.source_resource_version_id).filter((id): id is number => id !== null)
  const replace = async (ids: number[]) => { setBusy(true); setError(''); try { await put(`/api/sheets/${sheet.id}/resources`, { resource_version_ids: ids }); onChange(await api(`/api/sheets/${sheet.id}`)) } catch (reason) { setError(reason instanceof Error ? reason.message : 'La modification a échoué.') } finally { setBusy(false) } }
  const contribute = async () => {
    if (!instruction || !text.trim() || busy) return
    setBusy(true); setError('')
    try {
      const context = await api<{ sequence_id: number; situation_id: number; class_level: string }>(`/api/pedagogical-resources/contribution-context/${instruction.instruction_id}`)
      const created = await post<Resource>('/api/pedagogical-resources/user', { content: text, class_level: context.class_level, situation_id: context.situation_id, sequence_id: context.sequence_id, instruction_ids: [instruction.instruction_id], resource_type: 'APPLICATION_CONSIGNE', visibility_scope: visibility, title: 'Consigne personnelle' })
      await put(`/api/sheets/${sheet.id}/resources`, { resource_version_ids: [...selected, created.resource_version_id] })
      setText(''); setForm(false); await load(); onChange(await api(`/api/sheets/${sheet.id}`))
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'L’enregistrement a échoué.') } finally { setBusy(false) }
  }
  if (!instruction) return null
  return <section className="library-panel"><h3>Ressources de séance</h3><p className="muted">Propositions liées aux instructions de cette séance.</p>{error && <p role="alert">{error}</p>}<div className="resource-carousel">{items.filter(item => item.resource_type !== 'HOMEWORK_EXERCISE').map(item => <article className="resource-card" key={item.id}><span className="badge">{item.resource_type.replaceAll('_', ' ')}</span><h4>{item.title}</h4><LatexPreview content={item.content} compact /><small>{item.origin_type === 'USER_CONTRIBUTED' ? 'Contribution enseignant · Non revue' : 'Ressource vérifiée'}</small><button className="outline" disabled={sheet.status !== 'DRAFT' || busy} onClick={() => void replace(selected.includes(item.resource_version_id) ? selected.filter(id => id !== item.resource_version_id) : [...selected, item.resource_version_id])}>{selected.includes(item.resource_version_id) ? 'Retirer' : 'Ajouter'}</button></article>)}</div>{sheet.status === 'DRAFT' && <button className="outline" disabled={busy} onClick={() => setForm(value => !value)}>＋ Ajouter une consigne</button>}{form && <div className="local-box"><label>Texte<textarea value={text} onChange={event => setText(event.target.value)} /></label><label>Visibilité<select value={visibility} onChange={event => setVisibility(event.target.value)}><option value="PRIVATE">Privée</option><option value="SHARED">Partagée après validation</option></select></label><p>Origine : Contribution enseignant · Statut : Non revue</p><button className="primary" disabled={busy} onClick={() => void contribute()}>{busy ? 'Enregistrement…' : 'Enregistrer et ajouter'}</button></div>}</section>
}

export function HomeworkAndDocuments({ sheet, onChange }: { sheet: SheetDetail; onChange: (value: SheetDetail) => void }) {
  const [homework, setHomework] = useState<Resource[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [label, setLabel] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const load = async () => { const homeworkRows = await api<unknown>('/api/pedagogical-resources?resource_type=HOMEWORK_EXERCISE'); const documentRows = await api<unknown>(`/api/sheets/${sheet.id}/documents-used`); setHomework(Array.isArray(homeworkRows) ? homeworkRows.filter(row => row && typeof row === 'object' && 'resource_type' in row) as Resource[] : []); setDocuments(Array.isArray(documentRows) ? documentRows.filter(row => row && typeof row === 'object' && 'display_label' in row) as Document[] : []) }
  useEffect(() => { void load() }, [sheet.id])
  const selected = (sheet.homework || []).map(row => Number(row.snapshot.resource_id))
  const choose = async (resource: Resource, usage: string) => {
    const old = (sheet.homework || []).map(row => ({ pedagogical_resource_id: Number(row.snapshot.resource_id), homework_usage_type: row.homework_usage_type, teacher_note: row.teacher_note }))
    const items = selected.includes(resource.id) ? old.filter(row => row.pedagogical_resource_id !== resource.id) : [...old, { pedagogical_resource_id: resource.id, homework_usage_type: usage }]
    setBusy(true); setError(''); try { await put(`/api/sheets/${sheet.id}/homework`, { items }); onChange(await api(`/api/sheets/${sheet.id}`)); await load() } catch (reason) { setError(reason instanceof Error ? reason.message : 'La modification a échoué.') } finally { setBusy(false) }
  }
  const saveManual = async (values: Document[]) => { setBusy(true); setError(''); try { await put(`/api/sheets/${sheet.id}/documents-used`, { manual: values.filter(row => row.origin === 'MANUAL_REFERENCE') }); await load() } catch (reason) { setError(reason instanceof Error ? reason.message : 'La modification a échoué.') } finally { setBusy(false) } }
  return <div className="p3-planning">{error && <p role="alert">{error}</p>}<section><h3>Exercices de maison</h3><p className="muted">Une notion antérieure reste extérieure au périmètre de la séance.</p>{homework.map(item => <article className="instruction-row" key={item.id}><LatexPreview content={item.content} compact /><div><button className="outline" disabled={sheet.status !== 'DRAFT' || busy} onClick={() => void choose(item, 'CURRENT_SCOPE')}>{selected.includes(item.id) ? 'Retirer' : 'Notion actuelle'}</button>{!selected.includes(item.id) && <button className="link" disabled={sheet.status !== 'DRAFT' || busy} onClick={() => void choose(item, 'PRIOR_NOTION_REACTIVATION')}>Notion antérieure</button>}</div></article>)}</section><section><h3>Documents utilisés</h3>{documents.map((document, index) => <article className="instruction-row" key={`${document.origin}-${index}`}><div><b>{document.display_label}</b><small>{document.origin === 'AUTO_DERIVED' ? 'Ajout automatique' : 'Ajout manuel'}</small></div>{document.origin === 'MANUAL_REFERENCE' && sheet.status === 'DRAFT' && <button className="link" disabled={busy} onClick={() => void saveManual(documents.filter((_, position) => position !== index))}>Supprimer</button>}</article>)}{sheet.status === 'DRAFT' && <div className="local-box"><label>Ajouter un document manuel<input value={label} onChange={event => setLabel(event.target.value)} /></label><button className="outline" disabled={!label.trim() || busy} onClick={() => { void saveManual([...documents, { origin: 'MANUAL_REFERENCE', display_label: label }]); setLabel('') }}>Ajouter</button></div>}</section></div>
}
