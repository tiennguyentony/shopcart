# ADR-002: Use SQLite instead of PostgreSQL

**Status:** Accepted (supersedes the original Postgres + Redis setup)

## Context

The first version ran on Flask with PostgreSQL and a Redis cache for the
catalogue. New contributors spent their first day getting both running, and
the cache caused more stale-price bugs than it saved milliseconds. Our load
(a few hundred orders a day) is far below what one SQLite file handles.

## Decision

- Move to FastAPI and Python's built-in `sqlite3`. The database is one file
  whose path comes from `SHOPCART_DB` (default `shopcart.db`).
- Drop Redis. Catalogue queries hit SQLite directly.
- Migrations live in `migrations/` and run in filename order on startup. An
  applied migration is never edited; changes go in a new file.
- The app holds one connection. Writes that belong together run in a single
  `with conn:` block, which commits on success and rolls back on any exception.

## Consequences

- `uv sync && uv run pytest` works with no other services.
- Tests use `:memory:` databases, so they are fast and isolated.
- One process only; no concurrent writers across processes.
- Moving back to Postgres later means porting the migrations and the
  connection handling.
