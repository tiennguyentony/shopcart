def place_order(shop, headers, product_id, quantity=1) -> dict:
    shop.add_to_cart(headers, product_id, quantity)
    res = shop.client.post("/checkout", headers=headers)
    assert res.status_code == 201
    return res.json()


def test_list_my_orders(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug", stock=50)
    for _ in range(3):
        place_order(shop, headers, mug)

    body = shop.client.get("/orders", headers=headers).json()
    assert body["total"] == 3
    assert body["pages"] == 1


def test_order_count_only_includes_my_orders(shop):
    alice = shop.customer("alice@example.com")
    bob = shop.customer("bob@example.com")
    mug = shop.add_product("Mug", stock=50)
    place_order(shop, alice, mug)
    place_order(shop, bob, mug)
    place_order(shop, bob, mug)

    assert shop.client.get("/orders", headers=alice).json()["total"] == 1
    assert shop.client.get("/orders", headers=bob).json()["total"] == 2


def test_get_my_order(shop):
    headers = shop.customer()
    order = place_order(shop, headers, shop.add_product("Mug", price_cents=1400), quantity=2)

    res = shop.client.get(f"/orders/{order['id']}", headers=headers)
    assert res.status_code == 200
    assert res.json()["items"][0]["line_total_cents"] == 2800


def test_reorder_flag_follows_stock(shop):
    headers = shop.customer()
    lamp = shop.add_product("Lamp", stock=1)
    order = place_order(shop, headers, lamp)

    res = shop.client.get(f"/orders/{order['id']}", headers=headers)
    assert res.json()["items"][0]["can_reorder"] is False


def test_missing_order(shop):
    assert shop.client.get("/orders/999", headers=shop.customer()).status_code == 404


def test_admin_sees_all_orders(shop):
    alice = shop.customer("alice@example.com")
    bob = shop.customer("bob@example.com")
    admin = shop.admin()
    mug = shop.add_product("Mug", stock=50)
    place_order(shop, alice, mug)
    place_order(shop, bob, mug)

    body = shop.client.get("/admin/orders", headers=admin).json()
    assert body["total"] == 2


def test_customers_cannot_list_all_orders(shop):
    assert shop.client.get("/admin/orders", headers=shop.customer()).status_code == 403
