-- Core schema. Timestamps are ISO-8601 strings in UTC. Money is integer cents.

CREATE TABLE users (
  id            INTEGER PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
  created_at    TEXT NOT NULL
);

CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id),
  expires_at TEXT NOT NULL
);

CREATE TABLE products (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  category    TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  stock       INTEGER NOT NULL DEFAULT 0,
  published   INTEGER NOT NULL DEFAULT 0,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);

CREATE INDEX products_published ON products (published, id);

CREATE TABLE cart_items (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity   INTEGER NOT NULL CHECK (quantity > 0),
  added_at   TEXT NOT NULL
);

CREATE INDEX cart_items_user ON cart_items (user_id);

CREATE TABLE coupons (
  id              INTEGER PRIMARY KEY,
  code            TEXT NOT NULL UNIQUE,
  percent_off     INTEGER NOT NULL CHECK (percent_off BETWEEN 1 AND 100),
  max_uses        INTEGER,
  times_used      INTEGER NOT NULL DEFAULT 0,
  expires_at      TEXT
);

CREATE TABLE orders (
  id             INTEGER PRIMARY KEY,
  user_id        INTEGER NOT NULL REFERENCES users(id),
  status         TEXT NOT NULL DEFAULT 'PAID',
  subtotal_cents INTEGER NOT NULL,
  discount_cents INTEGER NOT NULL DEFAULT 0,
  shipping_cents INTEGER NOT NULL DEFAULT 0,
  total_cents    INTEGER NOT NULL,
  coupon_code    TEXT,
  created_at     TEXT NOT NULL
);

CREATE INDEX orders_user ON orders (user_id, id);

-- Name and price are copied at checkout so order history never changes.
CREATE TABLE order_items (
  id               INTEGER PRIMARY KEY,
  order_id         INTEGER NOT NULL REFERENCES orders(id),
  product_id       INTEGER NOT NULL REFERENCES products(id),
  product_name     TEXT NOT NULL,
  unit_price_cents INTEGER NOT NULL,
  quantity         INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE TABLE coupon_redemptions (
  id          INTEGER PRIMARY KEY,
  coupon_id   INTEGER NOT NULL REFERENCES coupons(id),
  order_id    INTEGER NOT NULL REFERENCES orders(id),
  user_id     INTEGER NOT NULL REFERENCES users(id),
  redeemed_at TEXT NOT NULL
);
