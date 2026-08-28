# MVP 4e — ready-to-test report

## Outcome

The project is a local modular monolith ready for user testing on Windows. It implements the complete pilot path from a guide instruction to candidate comparison, local snapshot adaptation, teacher/learner documents, finalization, execution and progress.

**Verdict: PASS — MVP 4E READY FOR USER TESTING.**

## Architecture and stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic.
- Database: SQLite for the tested local package; schema and ORM remain PostgreSQL-compatible.
- Frontend: React 19, TypeScript, Vite, KaTeX.
- Documents: server-side MiKTeX/pdfLaTeX with `-no-shell-escape`; explicit ReportLab fallback.
- Runtime: local-only `127.0.0.1`, no authentication in this personal MVP.

## Completed phases

M02 architecture/model, M03 bootstrap, M04 database/migration, M05 curriculum, M06 library, M07 teacher sheets, M08 learner supports, M09 LaTeX/TikZ/PDF, M10 execution/progress, M11 UX, M12 demo/E2E and M13 hardening are complete for the pilot slice.

Key commits:

- `62d689e` baseline;
- `16e3b28` M02 architecture;
- `00a7351` persistence and curriculum;
- `8620c28` resource/sheet frontend workflows;
- `d7f982e` demo, scripts and E2E;
- final M13 documentation/audit commit follows this report.

## Demo dataset

- ProgrammeVersion and GuideVersion 4e.
- SA1 and real guide Sequence 8 on algebraic expressions.
- Five knowledge/technique items and seven guide instructions.
- F-01..F-07 retained as open source issues; `PILOT-OBS-01` records the sample numbering observation.
- Four candidate resources: three sourced, one clearly non-sourced demo; atomic, composite, activity-complete and TikZ content are represented.
- One draft teacher sheet, one finalized/executed teacher sheet, one finalized learner support and an example progress record.

## Verification

- Backend: 18 passed, 0 failed.
- Frontend: 3 passed, 0 failed.
- Production build: PASS.
- E2E-001: PASS.
- Empty migration, idempotent seed, reset, one-click startup: PASS.
- Browser QA: dashboard, sources, library, comparison, eight-step editor, KaTeX/TikZ indicator and progress checked; no console errors/warnings.
- Three final PDF exports: LaTeX engine, A4, visually verified after correction.
- M01 matrix: 50/50 mapped; 34 tested, 9 implemented, 7 partial/non-blocking.

## Launch

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

- Frontend: `http://127.0.0.1:5173/`
- API docs: `http://127.0.0.1:8000/docs`
- Tester guide: `README_TESTER.md`
- Stop: `powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1`
- Reset: `powershell -ExecutionPolicy Bypass -File .\scripts\reset-demo.ps1`

## Important files

- `M01_FUNCTIONAL_DOMAIN_MODEL_FINAL_CANDIDATE.md` — frozen métier baseline.
- `docs/architecture/M01_INVARIANT_ENFORCEMENT_MATRIX.md` — invariant coverage.
- `backend/app/main.py` — local API.
- `backend/app/exporter.py` — safe LaTeX/PDF pipeline.
- `frontend/src/App.tsx` — non-technical workflow UI.
- `scripts/start-dev.ps1` — one-click startup.
- `docs/audits/MVP_READY_TO_TEST_AUDIT.md` — final audit.

Known non-blocking limitations are listed in `docs/KNOWN_LIMITATIONS.md`.
