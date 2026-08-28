# Technical decisions

M01 remains the normative authority. Technical decisions begin at M02 and must be recorded here with their rationale and consequences.

## Accepted M02 decisions

1. Modular monolith: FastAPI backend, React frontend, one transactionally consistent persistence layer.
2. SQLite for the immediately testable local build; PostgreSQL remains the compatible recommended target.
3. SQLAlchemy 2 + Alembic for persistence and migrations.
4. KaTeX for immediate browser math preview.
5. MiKTeX LaTeX compilation for real PDF where safe; ReportLab fallback remains explicit.
6. Local-only bind on `127.0.0.1`; no authentication in the personal MVP.
7. Server-owned export paths and restricted LaTeX compilation.

## Implementation decisions

8. A resource removed from the library uses `RETIRED`; it disappears from new selection while existing snapshots remain readable.
9. Finalized revision immutability is enforced both by application guards and a SQLAlchemy transaction guard.
10. Learner initial/completed output is selected from unique `BlockVariant.target` values without changing the support snapshot.
11. Contradictory 56 h / 60 h allocations remain separate; progress returns `UNRESOLVED_NORMATIVE_ALLOCATION` and no invented remainder.
12. Source LaTeX is saved independently from rendering. Dangerous file/process commands are rejected by the PDF renderer; compilation uses `-no-shell-escape`.
