import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class CartLine:
    id: int
    user_id: int
    product_id: int
    name: str
    unit_price_cents: int
    quantity: int

    @property
    def total_cents(self) -> int:
        return self.unit_price_cents * self.quantity


class CartRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def lines(self, user_id: int) -> list[CartLine]:
        rows = self.conn.execute(
            """
            SELECT c.id, c.user_id, c.product_id, p.name, p.price_cents AS unit_price_cents, c.quantity
            FROM cart_items c JOIN products p ON p.id = c.product_id
            WHERE c.user_id = ?
            ORDER BY c.id
            """,
            (user_id,),
        ).fetchall()
        return [CartLine(**row) for row in rows]

    def get_line(self, item_id: int) -> CartLine | None:
        row = self.conn.execute(
            """
            SELECT c.id, c.user_id, c.product_id, p.name, p.price_cents AS unit_price_cents, c.quantity
            FROM cart_items c JOIN products p ON p.id = c.product_id
            WHERE c.id = ?
            """,
            (item_id,),
        ).fetchone()
        return CartLine(**row) if row else None

    def add(self, user_id: int, product_id: int, quantity: int, now: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity, added_at) VALUES (?, ?, ?, ?)",
            (user_id, product_id, quantity, now),
        )
        return cur.lastrowid

    def set_quantity(self, item_id: int, quantity: int) -> None:
        self.conn.execute("UPDATE cart_items SET quantity = ? WHERE id = ?", (quantity, item_id))

    def remove(self, item_id: int) -> None:
        self.conn.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))

    def clear(self, user_id: int) -> None:
        self.conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
