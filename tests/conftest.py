from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from shopcart.clock import FakeClock, to_iso
from shopcart.config import Settings
from shopcart.db import open_database
from shopcart.main import AppDeps, create_app
from shopcart.repositories.coupons import CouponRepo
from shopcart.repositories.products import ProductRepo
from shopcart.repositories.users import UserRepo
from shopcart.services.auth import hash_password

# Monday 3 March 2031, 09:00 UTC.
T0 = datetime(2031, 3, 3, 9, 0, tzinfo=timezone.utc)
PASSWORD = "correct-horse"


@dataclass
class Shop:
    """A test app on an in-memory database, plus helpers to set up data."""

    client: TestClient
    conn: object
    clock: FakeClock
    settings: Settings
    password: str = PASSWORD

    def add_user(self, email: str, role: str = "customer") -> int:
        with self.conn:
            return UserRepo(self.conn).create(
                email, email.split("@")[0], hash_password(PASSWORD), role, to_iso(self.clock.now())
            )

    def login(self, email: str) -> dict[str, str]:
        res = self.client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert res.status_code == 200, res.text
        return {"Authorization": f"Bearer {res.json()['token']}"}

    def customer(self, email: str = "alice@example.com") -> dict[str, str]:
        self.add_user(email)
        return self.login(email)

    def admin(self) -> dict[str, str]:
        self.add_user("admin@example.com", role="admin")
        return self.login("admin@example.com")

    def add_product(
        self,
        name: str = "Mug",
        price_cents: int = 1000,
        stock: int = 10,
        published: bool = True,
        category: str = "kitchen",
    ) -> int:
        with self.conn:
            return ProductRepo(self.conn).create(
                name, "", category, price_cents, stock, published, to_iso(self.clock.now())
            )

    def add_coupon(self, code: str, percent_off: int, **kwargs) -> int:
        with self.conn:
            return CouponRepo(self.conn).create(code, percent_off, **kwargs)

    def add_to_cart(self, headers: dict[str, str], product_id: int, quantity: int = 1):
        return self.client.post(
            "/cart/items", json={"product_id": product_id, "quantity": quantity}, headers=headers
        )

    def stock_of(self, product_id: int) -> int:
        return ProductRepo(self.conn).get(product_id).stock


@pytest.fixture
def shop() -> Shop:
    conn = open_database(":memory:")
    clock = FakeClock(T0)
    settings = Settings(db_path=":memory:", seed_demo_data=False)
    app = create_app(AppDeps(conn=conn, clock=clock, settings=settings))
    with TestClient(app) as client:
        yield Shop(client=client, conn=conn, clock=clock, settings=settings)
    conn.close()
