# ADR-001 - Modular monolith

Decision: use one FastAPI backend and one React frontend with domain modules inside one deployable local application.

Rationale: the MVP needs strong transactions and simple local startup, not distributed coordination. Module boundaries preserve M01 concepts without microservice overhead.

Status: ACCEPTED.

