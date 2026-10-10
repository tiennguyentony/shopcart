import sqlite3
from dataclasses import dataclass

from shopcart.clock import Clock
from shopcart.config import Settings
from shopcart.domain.shipping import ShippingRule
from shopcart.repositories.carts import CartRepo
from shopcart.repositories.coupons import CouponRepo
from shopcart.repositories.orders import OrderRepo
from shopcart.repositories.products import ProductRepo
from shopcart.repositories.users import UserRepo
from shopcart.services.auth import AuthService
from shopcart.services.cart import CartService
from shopcart.services.catalog import CatalogService
from shopcart.services.checkout import CheckoutService
from shopcart.services.orders import OrderService


@dataclass(frozen=True)
class Services:
    auth: AuthService
    catalog: CatalogService
    cart: CartService
    checkout: CheckoutService
    orders: OrderService


def build_services(conn: sqlite3.Connection, clock: Clock, settings: Settings) -> Services:
    users = UserRepo(conn)
    products = ProductRepo(conn)
    carts = CartRepo(conn)
    orders = OrderRepo(conn)
    coupons = CouponRepo(conn)
    shipping = ShippingRule(
        flat_fee_cents=settings.shipping_fee_cents,
        free_threshold_cents=settings.free_shipping_threshold_cents,
    )
    return Services(
        auth=AuthService(conn, users, clock, settings.session_ttl_hours),
        catalog=CatalogService(conn, products, clock),
        cart=CartService(conn, carts, products, shipping, clock),
        checkout=CheckoutService(conn, carts, products, orders, coupons, shipping, clock),
        orders=OrderService(orders, products),
    )
