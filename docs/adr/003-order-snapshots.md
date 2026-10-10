# ADR-003: Orders keep a copy of what was bought

**Status:** Accepted

## Context

Products change after people buy them: prices go up or down, names are
edited, items are unpublished. If an order only pointed at `products`, an
old order would show today's price and name, and its line items would no
longer add up to what the customer paid.

## Decision

At checkout, each `order_items` row stores `product_name` and
`unit_price_cents` as they were at that moment, next to the `product_id`.
The order also stores its own `subtotal_cents`, `discount_cents`,
`shipping_cents` and `total_cents`.

Order history reads these stored values. The product row is only used for
things that are meant to be live, such as whether the item can be bought
again.

## Consequences

- An order looks the same forever, whatever happens to the catalogue.
- Some data is duplicated. That's intended.
- "My order shows a different price than the shop" is expected after a price
  change, and is not a bug.
