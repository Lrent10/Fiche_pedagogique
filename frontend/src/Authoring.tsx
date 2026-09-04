import { useEffect, useState } from 'react'
import { api, post, put } from './api'
import { LatexPreview } from './LatexPreview'
import type { SheetDetail, SupportDetail } from './types'

type Instruction = { id: number; text: string; code: string }
type Sequence = { id: number; title: string; instructions: Instruction[] }
type Situation = { id: number; title: string; sequences: Sequence[] }
type Curriculum = { id: number; level: string; title: string; situations: Situation[] }
type Source = { source_kind: string; source_ref: string; source_version: string; page_label?: string; adaptation?: boolean; validation_status?: string; author?: string }
type Candidate = { id: number; title: string; provenance: Source; blocks: { id: number; title: string; block_type: string; content_latex: string }[] }
type Preview = { identification: Record<string, string>; planning: Record<string, string>; instructions: Instruction[]; duration_conflict: boolean; durations: { hours: number; source_ref: string }[]; provenance: Record<string, { origin: string; sources: Source[] }> }
const sourceLabels: Record<string, string> = { OFFICIAL_PROGRAM: 'Programme officiel', OFFICIAL_GUIDE: 'Guide officiel', INSPECTOR_VALIDATED: 'Validation inspection', TEACHER_COMMUNITY: 'Communauté enseignante', BOOK_SOURCE: 'Livre', LOCAL_TEACHER: 'Création locale', DEMO_UNSOURCED: 'Démonstration non sourcée' }
const blockLabels: Record<string, string> = { INSTRUCTION: 'Consigne', CONSIGNE: 'Consigne', DEFINITION: 'Définition', PROPERTY: 'Propriété', FORMULA: 'Formule', METHOD: 'Méthode', FIGURE: 'Figure', EXPECTED_RESPONSE: 'Résultat attendu — enseignant', EXPECTED_TRACE: 'Trace attendue — enseignant', STATEMENT: 'Situation', APPLICATION: 'Application' }

export function SourceLabel({ source }: { source: Source }) {
  return <details className="source-detail"><summary>{sourceLabels[source.source_kind] || source.source_kind}{source.adaptation ? ' — adaptation à relire' : ''}{source.validation_status === 'INSPECTOR_VALIDATED' ? ' · Validée par inspection' : ''}</summary><p>{source.source_ref}{source.page_label && ` · p. ${source.page_label}`}</p><small>Version : {source.source_version}</small>{source.author && <p>Auteur : {source.author}</p>}</details>
}

export function AuthoringCreate({ onCreated }: { onCreated: (s: SheetDetail) => void }) {
  const [catalog, setCatalog] = useState<Curriculum[]>([])
  const [programmeId, setProgrammeId] = useState(0)
  const [saId, setSaId] = useState(0)
  const [sequenceId, setSequenceId] = useState(0)
  const [scope, setScope] = useState('SEQUENCE')
  const [instructionId, setInstructionId] = useState(0)
  const [selected, setSelected] = useState<number[]>([])
  const [title, setTitle] = useState('Produits remarquables — séance')
  const [preview, setPreview] = useState<Preview | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [local, setLocal] = useState<Record<string, string>>(() => { try { return JSON.parse(localStorage.getItem('fichemaths.teacher') || '{}') } catch { return {} } })
  const [savedLocal] = useState(local)
  const programme = catalog.find(p => p.id === programmeId)
  const sa = programme?.situations.find(s => s.id === saId)
  const sequence = sa?.sequences.find(s => s.id === sequenceId)
  const scopeId = scope === 'CLASS' ? programmeId : scope === 'SA' ? saId : scope === 'INSTRUCTION' ? instructionId : sequenceId
  useEffect(() => { api<Curriculum[]>('/api/authoring/curriculum').then(rows => { setCatalog(rows); setProgrammeId(rows[0]?.id || 0); setSaId(rows[0]?.situations[0]?.id || 0); setSequenceId(rows[0]?.situations[0]?.sequences[0]?.id || 0); setInstructionId(rows[0]?.situations[0]?.sequences[0]?.instructions[0]?.id || 0) }).catch(e => setError(String(e))) }, [])
  useEffect(() => {
    if (!scopeId || !programmeId) return
    let active = true
    setPreview(null)
    post<Preview>('/api/authoring/preview', { programme_id: programmeId, scope, scope_id: scopeId }).then(value => { if (active) { setPreview(value); setSelected(value.instructions.map(i => i.id)); setError('') } }).catch(e => { if (active) setError(String(e)) })
    return () => { active = false }
  }, [programmeId, scope, scopeId])
  async function create(automatic: boolean) {
    setBusy(true); setError('')
    try {
      const reused = Object.keys(local).filter(key => local[key] && local[key] === savedLocal[key])
      const result = await post<SheetDetail>('/api/authoring/compose', { programme_id: programmeId, scope, scope_id: scopeId, title, instruction_ids: selected, automatic, local, ...(reused.length ? { reused_local_fields: reused } : {}) })
      localStorage.setItem('fichemaths.teacher', JSON.stringify(local))
      onCreated(result)
    } catch (e) { setError(String(e)) } finally { setBusy(false) }
  }
  return <div className="authoring-create">
    <h3>Préparer depuis le programme</h3><p>Choisissez le périmètre, relisez l’identification et la planification, puis composez votre brouillon.</p>
    {error && <p role="alert" className="inline-error">{error}</p>}
    <div className="form-grid">
      <label>Titre de la séance<input required value={title} onChange={e => setTitle(e.target.value)} /></label>
      <label>Classe<select value={programmeId} onChange={e => { const p = catalog.find(x => x.id === Number(e.target.value)); setProgrammeId(p?.id || 0); setSaId(p?.situations[0]?.id || 0); setSequenceId(p?.situations[0]?.sequences[0]?.id || 0); setInstructionId(p?.situations[0]?.sequences[0]?.instructions[0]?.id || 0) }}>{catalog.map(p => <option key={p.id} value={p.id}>{p.level}</option>)}</select></label>
      <label>Périmètre<select value={scope} onChange={e => setScope(e.target.value)}><option value="CLASS">Parcourir la classe</option><option value="SA">Situation d’apprentissage</option><option value="SEQUENCE">Séquence</option><option value="INSTRUCTION">Instruction / activité</option></select></label>
      {scope !== 'CLASS' && <label>Situation d’apprentissage<select value={saId} onChange={e => { const s = programme?.situations.find(x => x.id === Number(e.target.value)); setSaId(s?.id || 0); setSequenceId(s?.sequences[0]?.id || 0); setInstructionId(s?.sequences[0]?.instructions[0]?.id || 0) }}>{programme?.situations.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}</select></label>}
      {['SEQUENCE', 'INSTRUCTION'].includes(scope) && <label>Séquence<select value={sequenceId} onChange={e => { const q = sa?.sequences.find(x => x.id === Number(e.target.value)); setSequenceId(q?.id || 0); setInstructionId(q?.instructions[0]?.id || 0) }}>{sa?.sequences.map(q => <option key={q.id} value={q.id}>{q.title}</option>)}</select></label>}
      {scope === 'INSTRUCTION' && <label>Instruction<select value={instructionId} onChange={e => setInstructionId(Number(e.target.value))}>{sequence?.instructions.map(i => <option key={i.id} value={i.id}>{i.text}</option>)}</select></label>}
    </div>
    {preview && <>
      <div className="curriculum-autofill"><h4>I. Identification issue du curriculum</h4>{Object.entries(preview.identification).map(([key, value]) => <p key={key}><b>{key} : </b>{value}</p>)}<h4>II. Planification issue des sources</h4>{Object.entries(preview.planning).map(([key, value]) => <div key={key}><b>{key}</b><p className="preserve-lines">{value}</p>{preview.provenance['planning.' + key]?.sources.map((source, index) => <SourceLabel key={index} source={source} />)}</div>)}</div>
      {preview.duration_conflict && <p className="info">Durée curriculaire à arbitrer : {preview.durations.map(d => `${d.hours} h (${d.source_ref})`).join(' / ')}. La durée de séance reste votre choix.</p>}
      <fieldset><legend>Instructions à préparer</legend>{preview.instructions.map(i => <label className="check" key={i.id}><input type="checkbox" checked={selected.includes(i.id)} onChange={() => setSelected(old => old.includes(i.id) ? old.filter(id => id !== i.id) : [...old, i.id])} /><LatexPreview content={i.text} compact /></label>)}</fieldset>
      <details><summary>Informations enseignant réutilisables</summary><p>Ces données locales restent modifiables et sont conservées dans ce navigateur.</p><div className="form-grid">{['nom du professeur', 'établissement', 'année scolaire'].map(key => <label key={key}>{key}<input value={local[key] || ''} onChange={e => setLocal({ ...local, [key]: e.target.value })} /></label>)}</div></details>
      {scope === 'CLASS' ? <p className="info">Choisissez une SA ou une séquence pour créer une fiche cohérente.</p> : <div className="final-buttons"><button className="outline" disabled={busy || !selected.length || !title.trim()} onClick={() => create(false)}>Commencer la conception →</button><button className="primary" disabled={busy || !selected.length || !title.trim()} onClick={() => create(true)}>Composition automatique</button></div>}
      <p className="muted">La composition crée un brouillon. La finalisation exige votre validation.</p>
    </>}
  </div>
}

export function InstructionChoices({ sheet, onChange }: { sheet: SheetDetail; onChange: (s: SheetDetail) => void }) {
  const [index, setIndex] = useState(0)
  const [rows, setRows] = useState<Candidate[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [title, setTitle] = useState('Ma consigne')
  const [content, setContent] = useState('')
  const [kind, setKind] = useState('INSTRUCTION')
  const current = sheet.segments[index]
  function load() { if (current) api<Candidate[]>(`/api/authoring/instructions/${current.instruction_id}/candidates`).then(setRows).catch(e => setError(String(e))) }
  useEffect(() => { let active = true; setRows([]); if (current) api<Candidate[]>(`/api/authoring/instructions/${current.instruction_id}/candidates`).then(value => { if (active) setRows(value) }).catch(e => setError(String(e))); return () => { active = false } }, [current?.instruction_id])
  if (!current) return null
  const selection = sheet.authoring?.selections?.[String(current.instruction_id)]
  async function choose(id: number) { setBusy(true); try { onChange(await put<SheetDetail>(`/api/authoring/sheets/${sheet.id}/selection`, { instruction_id: current.instruction_id, resource_version_id: id })); setError('') } catch (e) { setError(String(e)) } finally { setBusy(false) } }
  async function addLocal() { setBusy(true); try { await post('/api/authoring/resources', { title, level: sheet.curriculum_level || '4e', instruction_ids: [current.instruction_id], source_kind: 'LOCAL_TEACHER', source_ref: 'Création personnelle', source_version: '1', blocks: [{ title, block_type: kind, content_latex: content }] }); setContent(''); load() } catch (e) { setError(String(e)) } finally { setBusy(false) } }
  return <section className="instruction-choices"><h3>Instruction {index + 1}/{sheet.segments.length}</h3><LatexPreview content={current.text} /><div className="editor-nav"><button disabled={index === 0} onClick={() => setIndex(index - 1)}>Instruction précédente</button><button disabled={index === sheet.segments.length - 1} onClick={() => setIndex(index + 1)}>Instruction suivante</button></div>
    {error && <p role="alert">{error}</p>}{!rows.length && <p>Aucune ressource compatible disponible. Vous pouvez enregistrer une consigne personnelle.</p>}
    <div className="resource-grid">{rows.map(row => <article key={row.id} className="resource-card"><h4>{row.title}</h4><SourceLabel source={row.provenance} />{row.blocks.map(block => <div key={block.id}><small>{blockLabels[block.block_type] || block.block_type}</small><LatexPreview content={block.content_latex} compact /></div>)}<button disabled={busy || sheet.status !== 'DRAFT' || selection?.resource_version_id === row.id} onClick={() => choose(row.id)}>{selection?.resource_version_id === row.id ? 'Sélectionnée' : 'Choisir cette ressource'}</button></article>)}</div>
    {sheet.status === 'DRAFT' && <details className="local-box"><summary>Enregistrer une ressource personnelle pour cette instruction</summary><label>Type<select value={kind} onChange={e => setKind(e.target.value)}>{['INSTRUCTION', 'DEFINITION', 'PROPERTY', 'FORMULA', 'METHOD', 'APPLICATION', 'FIGURE'].map(k => <option value={k} key={k}>{blockLabels[k]}</option>)}</select></label><label>Titre<input value={title} onChange={e => setTitle(e.target.value)} /></label><label>Contenu LaTeX<textarea value={content} onChange={e => setContent(e.target.value)} /></label><LatexPreview content={content} /><button disabled={busy || !content.trim() || !title.trim()} onClick={addLocal}>Enregistrer dans ma bibliothèque</button></details>}
  </section>
}

export function LearnerFromSheet({ sheet }: { sheet: SheetDetail }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function generate() { setBusy(true); try { const support = await post<SupportDetail>(`/api/authoring/sheets/${sheet.id}/learner-support`); const pdf = await post<{ download_url: string }>('/api/exports', { document_family: 'LEARNER', revision_id: support.id, target: 'LEARNER_INITIAL' }); window.open(pdf.download_url, '_blank'); setError('Support créé dans Mes supports. Il reste modifiable.') } catch (e) { setError(String(e)) } finally { setBusy(false) } }
  return <div><button className="outline" disabled={busy} onClick={generate}>Créer le support apprenant (PDF)</button><p>Consignes, contenus de cours et figures, sans résultats attendus ni zones de réponse.</p>{error && <p role="status">{error}</p>}</div>
}
