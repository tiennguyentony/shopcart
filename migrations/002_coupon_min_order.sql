-- Coupons can require a minimum order value (before shipping).
ALTER TABLE coupons ADD COLUMN min_order_cents INTEGER NOT NULL DEFAULT 0;
