# Shopcart

Backend API for a small online shop selling homeware, stationery and apparel.

Customers browse the catalogue, fill a cart, apply a coupon and check out.
Admins manage products and see every order.

## Features

- Public catalogue with search, category filter and pagination
- Cart: add items, change quantities, remove items, live totals
- Coupons: percentage off, with expiry dates, usage limits and minimum order values
- Checkout creates the order, takes the stock and records the coupon redemption
- Flat-rate shipping, free above a threshold
- PayPal checkout
- Order history for customers; all orders for admins
- Redis cache in front of the product catalogue

## Tech stack

- Python 3.11+, [Flask](https://flask.palletsprojects.com)
- PostgreSQL 15
- Redis 7 (catalogue cache)
- pydantic for request validation
- pytest for tests

## Getting started

Requirements: Python 3.11+, a running PostgreSQL and Redis.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL=postgresql://localhost/shopcart
export REDIS_URL=redis://localhost:6379/0
flask run                     # http://localhost:5000
pytest
```

| Variable       | Default | Purpose                              |
|----------------|---------|--------------------------------------|
| `DATABASE_URL` | —       | Postgres connection string           |
| `REDIS_URL`    | —       | Redis for the catalogue cache        |
| `PAYPAL_CLIENT_ID` / `PAYPAL_SECRET` | — | PayPal REST credentials  |

On first start the database is seeded with demo data.

## Demo users

| Email               | Password   | Role     |
|---------------------|------------|----------|
| admin@shopcart.dev  | `admin123` | admin    |
| alice@example.com   | `alice123` | customer |
| bob@example.com     | `bob123`   | customer |

Demo coupons: `WELCOME` (10%, limited uses), `SAVE15` (15%), `BIGSPENDER`
(20% on orders over $100) and `SPRING20` (expired).

## API

Money is always integer cents (`price_cents`, `total_cents`, ...).

| Method | Path | Auth | Notes |
|---|---|---|---|
| `POST` | `/auth/login` | — | `{ "email", "password" }` → `{ "token" }` |
| `GET` | `/auth/me` | user | |
| `GET` | `/products?search=&category=&page=1&size=10` | — | published products only |
| `GET` | `/products/{id}` | — | |
| `GET` | `/cart` | user | items and totals |
| `POST` | `/cart/items` | user | `{ "product_id", "quantity" }` |
| `PATCH` | `/cart/items/{id}` | user | `{ "quantity" }` |
| `DELETE` | `/cart/items/{id}` | user | |
| `POST` | `/checkout` | user | `{ "coupon_code"? }` → the new order |
| `GET` | `/orders?page=1&size=10` | user | your orders, newest first |
| `GET` | `/orders/{id}` | user | |
| `POST` | `/admin/products` | admin | |
| `PATCH` | `/admin/products/{id}` | admin | any subset of fields |
| `GET` | `/admin/orders` | admin | |

Pages start at 1. Send the token as `Authorization: Bearer <token>`.

```bash
curl -X POST localhost:5000/auth/login -H 'content-type: application/json' \
  -d '{"email":"alice@example.com","password":"alice123"}'
```

## Project layout

```
src/shopcart/
  main.py           composition root (create_app)
  routes/           HTTP layer, request/response schemas
  services/         business logic
  repositories/     SQL
  domain/           pure rules: pricing, shipping, coupons, pagination
  seed.py           demo data
migrations/         schema, applied in order on startup
docs/adr/           architecture decision records
tests/              unit + integration tests
```

## Docs

Design decisions are recorded in [`docs/adr`](docs/adr).
