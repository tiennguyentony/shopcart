# ADR-001: Store money as integer cents

**Status:** Accepted

## Context

Floating-point numbers can't represent most decimal amounts exactly
(`0.1 + 0.2 != 0.3`). In a shop that shows up as totals that are off by a cent,
refunds that don't match charges, and reports that don't reconcile with the
payment provider.

## Decision

Every amount of money is an integer number of cents: in the database
(`price_cents`, `total_cents`, ...), in the domain code and in the API.
Percentages are applied with integer arithmetic and rounded half up to the
nearest cent, once, at a well-defined step.

Converting to dollars (dividing by 100) happens only when formatting text for
people, never in a calculation.

## Consequences

- Sums and differences are exact. A receipt always adds up.
- Every field name ends in `_cents`, so nobody has to guess the unit.
- Clients must format amounts themselves (`1999` → `$19.99`).
- Rounding has to be thought about explicitly whenever a percentage is applied.
