import sqlite3
from dataclasses import dataclass

from shopcart.domain.pagination import PageRequest
from shopcart.domain.pricing import Totals

ORDER_COLUMNS = (
    "id, user_id, status, subtotal_cents, discount_cents, shipping_cents, total_cents, "
    "coupon_code, created_at"
)


@dataclass(frozen=True)
class Order:
    id: int
    user_id: int
    status: str
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int
    coupon_code: str | None
    created_at: str


@dataclass(frozen=True)
class OrderItem:
    id: int
    order_id: int
    product_id: int
    product_name: str
    unit_price_cents: int
    quantity: int


class OrderRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, user_id: int, totals: Totals, coupon_code: str | None, now: str) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO orders
              (user_id, subtotal_cents, discount_cents, shipping_cents, total_cents, coupon_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                totals.subtotal_cents,
                totals.discount_cents,
                totals.shipping_cents,
                totals.total_cents,
                coupon_code,
                now,
            ),
        )
        return cur.lastrowid

    def add_item(
        self, order_id: int, product_id: int, product_name: str, unit_price_cents: int, quantity: int
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO order_items (order_id, product_id, product_name, unit_price_cents, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, product_id, product_name, unit_price_cents, quantity),
        )

    def get(self, order_id: int) -> Order | None:
        row = self.conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        return Order(**row) if row else None

    def items(self, order_id: int) -> list[OrderItem]:
        rows = self.conn.execute(
            """
            SELECT id, order_id, product_id, product_name, unit_price_cents, quantity
            FROM order_items WHERE order_id = ? ORDER BY id
            """,
            (order_id,),
        ).fetchall()
        return [OrderItem(**row) for row in rows]

    def list_for_user(self, user_id: int, page: PageRequest) -> tuple[list[Order], int]:
        total = self.conn.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        rows = self.conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (user_id, page.limit, page.offset),
        ).fetchall()
        return [Order(**row) for row in rows], total

    def list_all(self, page: PageRequest) -> tuple[list[Order], int]:
        total = self.conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        rows = self.conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM orders ORDER BY id DESC LIMIT ? OFFSET ?",
            (page.limit, page.offset),
        ).fetchall()
        return [Order(**row) for row in rows], total
