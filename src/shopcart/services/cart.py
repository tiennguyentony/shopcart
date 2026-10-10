import sqlite3
from dataclasses import dataclass

from shopcart.clock import Clock, to_iso
from shopcart.domain.errors import NotFound, OutOfStock
from shopcart.domain.pricing import Line, Totals, calculate_totals
from shopcart.domain.shipping import ShippingRule
from shopcart.repositories.carts import CartLine, CartRepo
from shopcart.repositories.products import ProductRepo


@dataclass(frozen=True)
class CartView:
    lines: list[CartLine]
    totals: Totals


class CartService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        carts: CartRepo,
        products: ProductRepo,
        shipping: ShippingRule,
        clock: Clock,
    ):
        self.conn = conn
        self.carts = carts
        self.products = products
        self.shipping = shipping
        self.clock = clock

    def view(self, user_id: int) -> CartView:
        lines = self.carts.lines(user_id)
        totals = calculate_totals(
            [Line(line.unit_price_cents, line.quantity) for line in lines], self.shipping
        )
        return CartView(lines=lines, totals=totals)

    def add_item(self, user_id: int, product_id: int, quantity: int) -> CartView:
        product = self.products.get(product_id)
        if product is None or not product.published:
            raise NotFound("Product")
        if quantity > product.stock:
            raise OutOfStock(product.name, product.stock)

        with self.conn:
            self.carts.add(user_id, product_id, quantity, now=to_iso(self.clock.now()))
        return self.view(user_id)

    def change_quantity(self, user_id: int, item_id: int, quantity: int) -> CartView:
        line = self._owned_line(user_id, item_id)
        product = self.products.get(line.product_id)
        if quantity > product.stock:
            raise OutOfStock(product.name, product.stock)

        with self.conn:
            self.carts.set_quantity(item_id, quantity)
        return self.view(user_id)

    def remove_item(self, user_id: int, item_id: int) -> CartView:
        self._owned_line(user_id, item_id)
        with self.conn:
            self.carts.remove(item_id)
        return self.view(user_id)

    def _owned_line(self, user_id: int, item_id: int) -> CartLine:
        line = self.carts.get_line(item_id)
        if line is None or line.user_id != user_id:
            raise NotFound("Cart item")
        return line
