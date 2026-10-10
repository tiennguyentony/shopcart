# ADR-004: Build the app in one place and inject its dependencies

**Status:** Accepted

## Context

Coupons expire, sessions time out and orders are time-stamped. Tests that
depend on the real clock or a shared database file are slow and flaky.

## Decision

`create_app(deps)` in `src/shopcart/main.py` is the only place that wires the
app together. `AppDeps` carries the database connection, the clock and the
settings. Services receive what they need through their constructors and
never open connections or call `datetime.now()` themselves.

Without arguments, `create_app()` reads settings from the environment, opens
the database file, runs migrations and seeds demo data if the database is
empty. Tests pass an in-memory database and a `FakeClock` instead.

## Consequences

- Time-based rules can be tested exactly (`shop.clock.advance(days=7)`).
- Adding a dependency means touching `AppDeps` and `build_services`.
- Anyone calling `datetime.now()` inside a service breaks testability.
  Reviewers should reject it.
