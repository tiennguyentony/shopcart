from datetime import timedelta

from shopcart.clock import to_iso
from shopcart.repositories.orders import OrderRepo


def count(shop, table: str) -> int:
    return shop.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_checkout_creates_an_order(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug", price_cents=1400, stock=10)
    pen = shop.add_product("Pen", price_cents=3400, stock=5)
    shop.add_to_cart(headers, mug, 2)
    shop.add_to_cart(headers, pen, 1)

    res = shop.client.post("/checkout", headers=headers)

    assert res.status_code == 201
    order = res.json()
    assert order["status"] == "PAID"
    assert order["subtotal_cents"] == 6200
    assert order["shipping_cents"] == 599
    assert order["total_cents"] == 6799
    assert [(i["name"], i["quantity"], i["unit_price_cents"]) for i in order["items"]] == [
        ("Mug", 2, 1400),
        ("Pen", 1, 3400),
    ]


def test_checkout_takes_stock_and_empties_the_cart(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug", stock=10)
    shop.add_to_cart(headers, mug, 3)

    shop.client.post("/checkout", headers=headers)

    assert shop.stock_of(mug) == 7
    assert shop.client.get("/cart", headers=headers).json()["items"] == []


def test_empty_cart_cannot_check_out(shop):
    res = shop.client.post("/checkout", headers=shop.customer())
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "EMPTY_CART"


def test_stock_sold_out_after_adding_to_cart(shop):
    alice = shop.customer("alice@example.com")
    bob = shop.customer("bob@example.com")
    lamp = shop.add_product("Lamp", stock=1)
    shop.add_to_cart(alice, lamp)
    shop.add_to_cart(bob, lamp)

    assert shop.client.post("/checkout", headers=alice).status_code == 201
    res = shop.client.post("/checkout", headers=bob)

    assert res.status_code == 409
    assert shop.stock_of(lamp) == 0
    assert len(shop.client.get("/cart", headers=bob).json()["items"]) == 1


def test_failed_checkout_leaves_nothing_behind(shop, monkeypatch):
    headers = shop.customer()
    mug = shop.add_product("Mug", stock=10)
    pen = shop.add_product("Pen", stock=10)
    shop.add_to_cart(headers, mug, 1)
    shop.add_to_cart(headers, pen, 1)

    calls = []

    def flaky_add_item(self, order_id, *args):
        calls.append(order_id)
        if len(calls) == 2:
            raise RuntimeError("disk full")
        return original(self, order_id, *args)

    original = OrderRepo.add_item
    monkeypatch.setattr(OrderRepo, "add_item", flaky_add_item)

    try:
        shop.client.post("/checkout", headers=headers)
    except RuntimeError:
        pass

    assert count(shop, "orders") == 0
    assert count(shop, "order_items") == 0
    assert shop.stock_of(mug) == 10
    assert len(shop.client.get("/cart", headers=headers).json()["items"]) == 2


def test_order_keeps_the_price_paid(shop):
    customer = shop.customer()
    admin = shop.admin()
    mug = shop.add_product("Mug", price_cents=1200)
    shop.add_to_cart(customer, mug, 2)
    order_id = shop.client.post("/checkout", headers=customer).json()["id"]

    shop.client.patch(f"/admin/products/{mug}", json={"price_cents": 1400, "name": "Big Mug"}, headers=admin)

    order = shop.client.get(f"/orders/{order_id}", headers=customer).json()
    assert order["items"][0]["unit_price_cents"] == 1200
    assert order["items"][0]["name"] == "Mug"
    assert order["subtotal_cents"] == 2400


def test_checkout_with_coupon(shop):
    headers = shop.customer()
    shop.add_coupon("TENOFF", 10)
    kettle = shop.add_product("Kettle", price_cents=5000)
    shop.add_to_cart(headers, kettle, 2)

    res = shop.client.post("/checkout", json={"coupon_code": "tenoff"}, headers=headers)

    assert res.status_code == 201
    order = res.json()
    assert order["coupon_code"] == "TENOFF"
    assert order["discount_cents"] == 1000
    assert order["shipping_cents"] == 0
    assert order["total_cents"] == 9000


def test_unknown_coupon(shop):
    headers = shop.customer()
    shop.add_to_cart(headers, shop.add_product("Mug"))
    res = shop.client.post("/checkout", json={"coupon_code": "NOPE"}, headers=headers)
    assert res.status_code == 422
    assert count(shop, "orders") == 0


def test_expired_coupon(shop):
    headers = shop.customer()
    shop.add_coupon("OLD", 10, expires_at=to_iso(shop.clock.now() - timedelta(hours=1)))
    shop.add_to_cart(headers, shop.add_product("Mug"))
    res = shop.client.post("/checkout", json={"coupon_code": "OLD"}, headers=headers)
    assert res.status_code == 422


def test_coupon_use_is_counted(shop):
    headers = shop.customer()
    coupon_id = shop.add_coupon("COUNTME", 10, max_uses=50)
    shop.add_to_cart(headers, shop.add_product("Mug"))
    shop.client.post("/checkout", json={"coupon_code": "COUNTME"}, headers=headers)

    times_used = shop.conn.execute("SELECT times_used FROM coupons WHERE id = ?", (coupon_id,)).fetchone()[0]
    assert times_used == 1
    assert count(shop, "coupon_redemptions") == 1
