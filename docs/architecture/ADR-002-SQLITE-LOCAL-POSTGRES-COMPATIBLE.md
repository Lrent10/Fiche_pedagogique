# ADR-002 - SQLite local, PostgreSQL compatible

Decision: use SQLite for the ready-to-test local build because no PostgreSQL server is currently available. Keep SQLAlchemy models, migrations and constraints portable to PostgreSQL.

Consequences: local startup is one-click. Concurrency certification against PostgreSQL is deferred and explicitly documented; no M01 invariant relies on SQLite-specific behavior.

Status: ACCEPTED FOR MVP LOCAL TESTING.

