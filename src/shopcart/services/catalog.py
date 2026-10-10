import sqlite3

from shopcart.clock import Clock, to_iso
from shopcart.domain.errors import NotFound
from shopcart.domain.pagination import PageRequest
from shopcart.repositories.products import Product, ProductRepo


class CatalogService:
    def __init__(self, conn: sqlite3.Connection, products: ProductRepo, clock: Clock):
        self.conn = conn
        self.products = products
        self.clock = clock

    def list_published(
        self, page: PageRequest, search: str | None = None, category: str | None = None
    ) -> tuple[list[Product], int]:
        return self.products.list_published(page, search=search, category=category)

    def get_published(self, product_id: int) -> Product:
        product = self.products.get(product_id)
        if product is None or not product.published:
            raise NotFound("Product")
        return product

    def create(self, **fields) -> Product:
        with self.conn:
            product_id = self.products.create(**fields, now=to_iso(self.clock.now()))
        return self.products.get(product_id)

    def update(self, product_id: int, changes: dict[str, object]) -> Product:
        if self.products.get(product_id) is None:
            raise NotFound("Product")
        with self.conn:
            self.products.update(product_id, changes, now=to_iso(self.clock.now()))
        return self.products.get(product_id)
