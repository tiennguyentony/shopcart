def test_cart_starts_empty(shop):
    body = shop.client.get("/cart", headers=shop.customer()).json()
    assert body["items"] == []
    assert body["total_cents"] == 0


def test_add_items_and_see_totals(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug", price_cents=1400)
    towel = shop.add_product("Tea Towel", price_cents=1999)

    shop.add_to_cart(headers, mug, 2)
    res = shop.add_to_cart(headers, towel, 1)

    assert res.status_code == 201
    body = res.json()
    assert [(i["name"], i["quantity"]) for i in body["items"]] == [("Mug", 2), ("Tea Towel", 1)]
    assert body["subtotal_cents"] == 4799
    assert body["shipping_cents"] == 599
    assert body["total_cents"] == 5398


def test_free_shipping_in_cart(shop):
    headers = shop.customer()
    jacket = shop.add_product("Rain Jacket", price_cents=8900)
    body = shop.add_to_cart(headers, jacket).json()
    assert body["shipping_cents"] == 0


def test_change_quantity(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug", price_cents=1400)
    item_id = shop.add_to_cart(headers, mug).json()["items"][0]["id"]

    res = shop.client.patch(f"/cart/items/{item_id}", json={"quantity": 3}, headers=headers)
    assert res.status_code == 200
    assert res.json()["items"][0]["quantity"] == 3
    assert res.json()["subtotal_cents"] == 4200


def test_remove_item(shop):
    headers = shop.customer()
    mug = shop.add_product("Mug")
    item_id = shop.add_to_cart(headers, mug).json()["items"][0]["id"]

    res = shop.client.delete(f"/cart/items/{item_id}", headers=headers)
    assert res.json()["items"] == []


def test_cannot_add_more_than_stock(shop):
    headers = shop.customer()
    pen = shop.add_product("Pen", stock=2)
    res = shop.add_to_cart(headers, pen, 3)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "OUT_OF_STOCK"


def test_cannot_add_unpublished_product(shop):
    headers = shop.customer()
    secret = shop.add_product("Secret", published=False)
    assert shop.add_to_cart(headers, secret).status_code == 404


def test_cannot_edit_someone_elses_cart(shop):
    alice = shop.customer("alice@example.com")
    bob = shop.customer("bob@example.com")
    mug = shop.add_product("Mug")
    item_id = shop.add_to_cart(alice, mug).json()["items"][0]["id"]

    res = shop.client.patch(f"/cart/items/{item_id}", json={"quantity": 5}, headers=bob)
    assert res.status_code == 404
    assert shop.client.delete(f"/cart/items/{item_id}", headers=bob).status_code == 404


def test_cart_needs_login(shop):
    assert shop.client.get("/cart").status_code == 401
