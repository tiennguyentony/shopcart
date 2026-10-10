import sqlite3
from datetime import datetime

from shopcart.clock import Clock, to_iso
from shopcart.domain.coupons import Coupon, check_coupon
from shopcart.domain.errors import EmptyCart, InvalidCoupon, NotFound, OutOfStock
from shopcart.domain.pricing import Line, calculate_totals, subtotal_cents
from shopcart.domain.shipping import ShippingRule
from shopcart.repositories.carts import CartRepo
from shopcart.repositories.coupons import CouponRepo
from shopcart.repositories.orders import OrderRepo
from shopcart.repositories.products import ProductRepo


class CheckoutService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        carts: CartRepo,
        products: ProductRepo,
        orders: OrderRepo,
        coupons: CouponRepo,
        shipping: ShippingRule,
        clock: Clock,
    ):
        self.conn = conn
        self.carts = carts
        self.products = products
        self.orders = orders
        self.coupons = coupons
        self.shipping = shipping
        self.clock = clock

    def checkout(self, user_id: int, coupon_code: str | None = None) -> int:
        """Turns the user's cart into a paid order and returns the order id.

        Everything happens in one transaction: if any step fails, no order is
        created, no stock moves and the cart is left as it was.
        """
        now = self.clock.now()
        with self.conn:
            lines = self.carts.lines(user_id)
            if not lines:
                raise EmptyCart()

            products = self.products.get_many([line.product_id for line in lines])
            for line in lines:
                product = products.get(line.product_id)
                if product is None or not product.published:
                    raise NotFound(f"Product {line.product_id}")
                if line.quantity > product.stock:
                    raise OutOfStock(product.name, product.stock)

            priced = [Line(line.unit_price_cents, line.quantity) for line in lines]
            coupon = self._usable_coupon(coupon_code, subtotal_cents(priced), now)
            totals = calculate_totals(priced, self.shipping, coupon.percent_off if coupon else 0)

            order_id = self.orders.create(user_id, totals, coupon.code if coupon else None, to_iso(now))
            for line in lines:
                self.orders.add_item(
                    order_id, line.product_id, line.name, line.unit_price_cents, line.quantity
                )
                self.products.decrement_stock(line.product_id, line.quantity)
            if coupon:
                self.coupons.record_redemption(coupon.id, order_id, user_id, to_iso(now))
            self.carts.clear(user_id)
        return order_id

    def _usable_coupon(self, code: str | None, subtotal: int, now: datetime) -> Coupon | None:
        if not code:
            return None
        coupon = self.coupons.by_code(code)
        if coupon is None:
            raise InvalidCoupon(f"Unknown coupon {code}")
        check_coupon(coupon, subtotal, now)
        return coupon
