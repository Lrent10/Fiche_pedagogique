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

