import sqlite3

from shopcart.clock import from_iso
from shopcart.domain.coupons import Coupon


class CouponRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def by_code(self, code: str) -> Coupon | None:
        row = self.conn.execute(
            """
            SELECT id, code, percent_off, max_uses, times_used, min_order_cents, expires_at
            FROM coupons WHERE code = ?
            """,
            (code.strip().upper(),),
        ).fetchone()
        if row is None:
            return None
        expires_at = from_iso(row["expires_at"]) if row["expires_at"] else None
        return Coupon(**{**dict(row), "expires_at": expires_at})

    def create(
        self,
        code: str,
        percent_off: int,
        max_uses: int | None = None,
        min_order_cents: int = 0,
        expires_at: str | None = None,
        times_used: int = 0,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO coupons (code, percent_off, max_uses, times_used, min_order_cents, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code.upper(), percent_off, max_uses, times_used, min_order_cents, expires_at),
        )
        return cur.lastrowid

    def record_redemption(self, coupon_id: int, order_id: int, user_id: int, now: str) -> None:
        self.conn.execute("UPDATE coupons SET times_used = times_used + 1 WHERE id = ?", (coupon_id,))
        self.conn.execute(
            "INSERT INTO coupon_redemptions (coupon_id, order_id, user_id, redeemed_at) VALUES (?, ?, ?, ?)",
            (coupon_id, order_id, user_id, now),
        )
