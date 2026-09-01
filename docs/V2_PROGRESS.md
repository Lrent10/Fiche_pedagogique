# V2-01 / V2-02 / V2-02B progress

Status: V2-02B human UX and document finalization complete with non-blocking layout items.

## Baseline preserved

- Baseline commit: `15e03daeb74e4833863579d2bab7cf260d30605a`.
- V1 checkpoint: `mvp-4e-v1-ready-to-test`.
- Working branch: `feature/v2-document-fidelity-support-first`.
- Frozen M01 SHA-256: `03F54F7C62A0E6F2F3BE154631EE542408BF5423B5D4FAD8B147CD85CE0E3B67`.
- M01 source document was not modified.

## Delivered

- Dense A4 portrait teacher template with identification, planning and session flow.
- A4 portrait learner template with serif typography, two columns, central rule, lightweight headers/footers and pedagogical block styles.
- Manual LaTeX expected results stored on each relevant flow item and copied into new teacher revisions.
- Support-first endpoint and UI: finalized support revision, explicit block selection, duration estimate, teacher-sheet creation.
- `SupportUse` stores the exact support revision, selected source block IDs, part label and linked teacher revision.
- Initial learner export masks teacher-only/solution blocks; completed export renders completed variants.
- Alembic revision `0002_v2_document_workflow`.
- Automated `DOC-001..010` and `WF-001..003` coverage.
- Rendered PNG evidence under `docs/audits/visual/`.
- Final whole-document editor with structure, live preview, block editing, visibility and ordering.
- Human-readable LaTeX validation and empty-support finalization guard.
- Local typed blocks in the support editor for author-driven long documents.
- Natural user-document labels and removal of technical export traces.
- Reliable start/stop PID handling and fail-fast aggregate test script.
- Human UX and three-page PDF evidence under `docs/audits/human-ux/`.

## Final verification

- Backend: 34 passed, 0 failed.
- Frontend: 3 passed, 0 failed.
- Production build: PASS.
- Alembic upgrade to `0002_v2_document_workflow`: PASS.
- Backend and frontend startup probes: HTTP 200 / HTTP 200.
- Three representative PDFs: LaTeX engine, A4 portrait, visual QA PASS.
- Long support: initial 3 pages, completed 3 pages, 3 activities and 7 printed consignes.
- Final teacher sheet: 1 page, natural French labels, no internal identifier in document text.
- V2-02B verdict: `PASS_WITH_NON_BLOCKING_ITEMS` (column-width figures and optional response-space compaction).

## Explicit exclusions respected

- M01 was not reopened or edited.
- No AI feature or automatic expected-result generation was added.
- No 4e resource ingestion was run.
- No multi-class architecture was introduced.
- Source PDFs were not modified.
