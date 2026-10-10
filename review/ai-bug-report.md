# Shopcart code review

> Prompt: "Here is our shop backend (src/ and tests/ attached). Find the bugs,
> ordered by severity, with a suggested fix for each."

I reviewed the FastAPI app, the repositories, the services and the domain
modules. Overall the structure is clean (routes, services, repositories,
domain), but I found several issues worth fixing before this handles real
customers.

## 1. SQL injection in product updates (Critical)

**File:** `src/shopcart/repositories/products.py`, `ProductRepo.update`

The `UPDATE` statement is built with an f-string:

```python
assignments = ", ".join(f"{name} = ?" for name in fields)
self.conn.execute(f"UPDATE products SET {assignments}, updated_at = ? WHERE id = ?", ...)
```

Building SQL with string interpolation allows an attacker to inject arbitrary
SQL through the request body of `PATCH /admin/products/{id}`.

**Fix:** never build SQL with f-strings. Write one fixed `UPDATE` statement
that sets every column, and pass all values as parameters.

## 2. Order history shows outdated prices (High)

**File:** `src/shopcart/services/orders.py`, `OrderService._view`

Order lines use `item.unit_price_cents` and `item.product_name` from the
`order_items` table instead of the product's current data. When an admin
changes a price or renames a product, customers see stale information on
their order page, and the data in `order_items` drifts away from the catalogue.

**Fix:** read name and price from the product you already load for
`can_reorder`:

```python
product = self.products.get(item.product_id)
name = product.name if product else item.product_name
unit_price = product.price_cents if product else item.unit_price_cents
```

## 3. Any logged-in user can read any order (High)

**File:** `src/shopcart/routes/orders.py`, `get_order`

The route requires a logged-in user but never checks that the order belongs
to them. Order ids are sequential, so a customer can read other customers'
orders by changing the number in the URL.

**Fix:** load the order and raise `Forbidden` (403) if
`order.user_id != user.id` and the user is not an admin.

## 4. Checkout is not atomic (Medium)

**File:** `src/shopcart/services/checkout.py`, `CheckoutService.checkout`

Checkout performs several writes (create order, add items, decrement stock,
record coupon, clear cart) without an explicit transaction. If the process
fails halfway, you can end up with an order but no items, or stock taken for
an order that doesn't exist. This is also how stock can go negative under
load.

**Fix:** wrap the writes in an explicit transaction:

```python
self.conn.execute("BEGIN")
try:
    ...
    self.conn.commit()
except Exception:
    self.conn.rollback()
    raise
```

## 5. Free shipping threshold is misconfigured (Medium)

**File:** `src/shopcart/config.py`

`ShippingRule` documents that orders of $50.00 or more ship free, but
`Settings.free_shipping_threshold_cents` is `7500` ($75.00). Customers with
orders between $50 and $75 are charged shipping they shouldn't pay.

**Fix:** set `free_shipping_threshold_cents: int = 5000` and update
`test_free_shipping_threshold_is_75_dollars` to match.

## 6. Session tokens stored in plain text (Low)

**File:** `src/shopcart/repositories/users.py`, `create_session`

Session tokens are written straight to the `sessions` table. Anyone who gets
a copy of the database can impersonate every logged-in user.

**Fix:** store a SHA-256 hash of the token and compare hashes on lookup.

## Things that look good

- **Money handling.** Amounts are integer cents throughout, and
  `apply_percent_off` rounds the discount to the nearest cent with `round()`,
  so totals are exact. No change needed.
- **Pagination.** `PageRequest` validates page and size and caps the size at
  100. Page counts round up correctly.
- **Coupons.** `check_coupon` covers expiry, usage limits and minimum order
  value, and the error messages are clear.
- **Tests.** The suite uses an in-memory database and a fake clock, which
  keeps it fast and deterministic.

Let me know if you'd like me to apply any of these fixes.
