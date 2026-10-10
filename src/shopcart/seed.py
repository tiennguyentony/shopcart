"""Demo data, loaded on startup when the database is empty."""

import sqlite3
from datetime import timedelta

from shopcart.clock import Clock, to_iso
from shopcart.domain.pricing import Totals
from shopcart.repositories.coupons import CouponRepo
from shopcart.repositories.orders import OrderRepo
from shopcart.repositories.products import ProductRepo
from shopcart.repositories.users import UserRepo
from shopcart.services.auth import hash_password

USERS = [
    ("admin@shopcart.dev", "Ada Admin", "admin123", "admin"),
    ("alice@example.com", "Alice Martin", "alice123", "customer"),
    ("bob@example.com", "Bob Chen", "bob123", "customer"),
]

# (name, category, price_cents, stock, published, description)
PRODUCTS = [
    ("Ceramic Mug", "kitchen", 1400, 40, True, "350 ml stoneware mug, dishwasher safe."),
    ("Linen Tea Towel Set", "kitchen", 1999, 25, True, "Set of three washed-linen tea towels."),
    ("Bamboo Cutting Board", "kitchen", 2450, 18, True, "Large board with a juice groove."),
    ("Pour-Over Coffee Kit", "kitchen", 3899, 12, True, "Glass dripper, filters and a scoop."),
    ("Cast Iron Skillet", "kitchen", 4500, 8, True, "26 cm pre-seasoned skillet."),
    ("Enamel Water Bottle", "kitchen", 1650, 30, True, "Keeps drinks cold for 12 hours."),
    ("Dot Grid Notebook", "stationery", 1299, 60, True, "A5, 160 pages, lay-flat binding."),
    ("Brass Pen", "stationery", 3400, 15, True, "Refillable ballpoint, ages beautifully."),
    ("Desk Organiser", "stationery", 2199, 20, True, "Walnut tray with three compartments."),
    ("Washi Tape Pack", "stationery", 799, 80, True, "Ten rolls in muted colours."),
    ("Weekly Planner 2027", "stationery", 1850, 35, True, "Undated weekly spreads, linen cover."),
    ("Fountain Pen Ink", "stationery", 1150, 3, True, "50 ml bottle, deep blue-black."),
    ("Organic Cotton Tee", "apparel", 2500, 50, True, "Heavyweight crew neck, unisex sizing."),
    ("Merino Beanie", "apparel", 2899, 22, True, "Fine-knit merino wool, one size."),
    ("Canvas Tote Bag", "apparel", 1599, 45, True, "Sturdy tote with an inside pocket."),
    ("Wool Socks (2 pairs)", "apparel", 1799, 40, True, "Cushioned hiking socks."),
    ("Rain Jacket", "apparel", 8900, 6, True, "Packable, fully seam-sealed."),
    ("Linen Throw Pillow", "home", 3200, 14, True, "45 x 45 cm cover with feather insert."),
    ("Soy Wax Candle", "home", 2200, 28, True, "Cedar and fig, 40 hour burn time."),
    ("Wool Throw Blanket", "home", 7900, 9, True, "Lambswool throw, 130 x 180 cm."),
    ("Ceramic Planter", "home", 2750, 16, True, "Matte glaze planter with drainage tray."),
    ("Wall Clock", "home", 4200, 2, True, "Silent sweep movement, 30 cm."),
    ("Smart Mug Prototype", "kitchen", 12900, 5, False, "Heated mug. Not ready for sale."),
    ("Winter Scarf (coming soon)", "apparel", 3900, 0, False, "Launches in November."),
]


def seed_if_empty(conn: sqlite3.Connection, clock: Clock) -> bool:
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return False

    now = clock.now()
    users, products = UserRepo(conn), ProductRepo(conn)
    coupons, orders = CouponRepo(conn), OrderRepo(conn)

    with conn:
        user_ids = {
            email: users.create(email, name, hash_password(pw), role, to_iso(now))
            for email, name, pw, role in USERS
        }
        for name, category, price, stock, published, description in PRODUCTS:
            products.create(name, description, category, price, stock, published, to_iso(now))

        coupons.create("WELCOME", 10, max_uses=100, times_used=23)
        coupons.create("SAVE15", 15)
        coupons.create("BIGSPENDER", 20, min_order_cents=10000)
        coupons.create("SPRING20", 20, expires_at=to_iso(now - timedelta(days=30)))

        # Alice bought two mugs back when they cost $12.00.
        last_month = to_iso(now - timedelta(days=30))
        order_id = orders.create(
            user_ids["alice@example.com"], Totals(2400, 0, 599, 2999), None, last_month
        )
        orders.add_item(order_id, 1, "Ceramic Mug", 1200, 2)

        order_id = orders.create(
            user_ids["bob@example.com"], Totals(8900, 0, 0, 8900), None, to_iso(now - timedelta(days=3))
        )
        orders.add_item(order_id, 17, "Rain Jacket", 8900, 1)
    return True
