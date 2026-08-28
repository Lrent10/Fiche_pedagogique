# M02-A - Technical architecture

Status: FROZEN FOR MVP IMPLEMENTATION

## Context and goals

The application is a local Windows-first tool translating the frozen M01 domain model. It must be immediately testable, preserve version history, support editable LaTeX, export real PDFs, and avoid infrastructure that is unnecessary for one local user.

## Chosen architecture

```text
React + TypeScript + Vite
          |
          | JSON/HTTP on 127.0.0.1
          v
FastAPI modular monolith
  - curriculum
  - library and provenance
  - teacher sheets
  - learner supports
  - execution/progress
  - rendering/exports
          |
          v
SQLAlchemy unit of work
          |
          v
SQLite local MVP (PostgreSQL-compatible model)
```

No microservice, message broker, remote account, public listener, or generative AI is introduced.

## Stack

| Concern | Choice | Rationale |
|---|---|---|
| Backend | Python 3.12, FastAPI, Pydantic | Typed, testable local API |
| Persistence | SQLAlchemy 2, Alembic | Explicit transactions and migration path |
| Local database | SQLite | No PostgreSQL daemon is available; zero-setup local testing |
| Target compatibility | PostgreSQL | Portable SQLAlchemy types; no SQLite-only business model |
| Frontend | React 19, TypeScript, Vite | Fast desktop-first workflow and component tests |
| Math preview | KaTeX in browser | Immediate feedback without server round trip |
| PDF | LaTeX via MiKTeX when possible; ReportLab fallback | Real PDF remains available if TeX rendering fails |
| Tests | pytest, Vitest, Testing Library, Playwright/manual fallback | Layered verification |

## Module boundaries

- `curriculum`: ProgrammeVersion, GuideVersion, SA, Sequence, KnowledgeItem, InstructionGuide, allocations.
- `sources`: SourceDocument, SourceOccurrence, SourceIssue, ProposedContent.
- `library`: PedagogicalResource, version, block, variant, instruction mapping.
- `teacher`: sheet identity, immutable revisions, segments, resource/block instances, flow and phases.
- `support`: support identity, immutable revisions, local instances, block instances and uses.
- `execution`: TeachingSession, executed segments and derived progress.
- `exports`: source-exclusive DocumentExport and rendering.

Modules share one transaction boundary but cannot mutate another module's finalized history.

## Transactions

- One HTTP command is one transaction.
- Snapshot creation copies source blocks in the same transaction as the owning local instance.
- Finalization validates the complete aggregate and changes state atomically.
- Export metadata is committed only after a file exists; failures are recorded explicitly.
- Demo reset operates only on the configured local database and export folder.

## Versioning and immutability

- Library versions, teacher revisions and support revisions use stable identities plus numbered versions/revisions.
- Finalized revisions reject update/delete operations at domain and API layers.
- Local instances keep nullable source references qualified by the mandatory origin discriminator.
- Snapshots copy editable content; later library versions never update old snapshots.
- Retired library versions remain readable and historically referenced.

## Files and images

- Source documents remain outside the repository and are referenced by metadata/path configuration.
- Generated exports live under `exports/` and are ignored by Git.
- Temporary TeX compilation lives under `tmp/latex/` and is cleanable.
- MVP image blocks accept safe local/demo URLs only; uploads are not exposed in the first slice.

## LaTeX and TikZ

- Source text is always stored before preview/rendering.
- KaTeX renders ordinary math in the browser and shows an error without deleting source.
- Server PDF rendering uses a restricted LaTeX template with `-no-shell-escape`.
- Dangerous document-level commands in editable fragments are rejected for compilation but the source remains saved.
- TikZ uses server TeX when the required package is available; otherwise the source and a visible limited-preview state remain.

## Security and local safety

- Bind to `127.0.0.1` only.
- No authentication is added for the personal local MVP.
- CORS allows only the local frontend origin.
- Export paths are server-generated; callers cannot choose arbitrary filesystem paths.
- LaTeX runs without shell escape and with a deny-list for file/document commands.
- No source PDF is modified.

## Test strategy

1. Domain tests for origins, snapshots, immutability, variants, durations and progression.
2. Persistence/migration tests from an empty database.
3. API tests for the complete vertical slice.
4. Frontend component and workflow tests.
5. Browser E2E for create, compare, adapt, warn, finalize, export and execute.
6. Visual inspection of the local UI and representative PDFs.

## M02-A gate

- Architecture complete: PASS
- M01 contradiction: NONE
- LaTeX strategy: DEFINED
- Files/images strategy: DEFINED
- Transactions: DEFINED
- Versioning: DEFINED
- Tests: DEFINED

