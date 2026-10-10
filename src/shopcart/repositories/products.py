import sqlite3
from dataclasses import dataclass

from shopcart.domain.pagination import PageRequest

COLUMNS = "id, name, description, category, price_cents, stock, published"


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    description: str
    category: str
    price_cents: int
    stock: int
    published: bool


def _to_product(row: sqlite3.Row) -> Product:
    return Product(**{**dict(row), "published": bool(row["published"])})


class ProductRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get(self, product_id: int) -> Product | None:
        row = self.conn.execute(f"SELECT {COLUMNS} FROM products WHERE id = ?", (product_id,)).fetchone()
        return _to_product(row) if row else None

    def get_many(self, ids: list[int]) -> dict[int, Product]:
        if not ids:
            return {}
        placeholders = ", ".join("?" for _ in ids)
        rows = self.conn.execute(
            f"SELECT {COLUMNS} FROM products WHERE id IN ({placeholders})", ids
        ).fetchall()
        return {row["id"]: _to_product(row) for row in rows}

    def list_published(
        self, page: PageRequest, search: str | None = None, category: str | None = None
    ) -> tuple[list[Product], int]:
        where = ["published = 1"]
        params: list[object] = []
        if category:
            where.append("category = ?")
            params.append(category)
        if search:
            where.append(f"name LIKE '%{search}%'")
        conditions = " AND ".join(where)

        total = self.conn.execute(
            f"SELECT COUNT(*) FROM products WHERE {conditions}", params
        ).fetchone()[0]
        rows = self.conn.execute(
            f"""
            SELECT {COLUMNS} FROM products
            WHERE {conditions}
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            [*params, page.limit, page.offset],
        ).fetchall()
        return [_to_product(row) for row in rows], total

    def create(
        self,
        name: str,
        description: str,
        category: str,
        price_cents: int,
        stock: int,
        published: bool,
        now: str,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO products
              (name, description, category, price_cents, stock, published, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, description, category, price_cents, stock, int(published), now, now),
        )
        return cur.lastrowid

    def update(self, product_id: int, changes: dict[str, object], now: str) -> None:
        allowed = {"name", "description", "category", "price_cents", "stock", "published"}
        fields = {k: v for k, v in changes.items() if k in allowed}
        if not fields:
            return
        assignments = ", ".join(f"{name} = ?" for name in fields)
        self.conn.execute(
            f"UPDATE products SET {assignments}, updated_at = ? WHERE id = ?",
            [*fields.values(), now, product_id],
        )

    def decrement_stock(self, product_id: int, quantity: int) -> None:
        self.conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id)
        )
