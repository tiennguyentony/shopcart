def test_listing_counts_only_published_products(shop):
    shop.add_product("Mug")
    shop.add_product("Plate")
    shop.add_product("Secret Prototype", published=False)

    body = shop.client.get("/products").json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert all(p["name"] != "Secret Prototype" for p in body["items"])


def test_search_by_name(shop):
    shop.add_product("Ceramic Mug")
    shop.add_product("Travel Mug")
    shop.add_product("Notebook")

    body = shop.client.get("/products", params={"search": "mug"}).json()
    assert body["total"] == 2
    assert body["pages"] == 1


def test_filter_by_category(shop):
    shop.add_product("Mug", category="kitchen")
    shop.add_product("Tee", category="apparel")

    body = shop.client.get("/products", params={"category": "apparel"}).json()
    assert body["total"] == 1


def test_page_count(shop):
    for i in range(25):
        shop.add_product(f"Product {i}")
    body = shop.client.get("/products", params={"size": 10}).json()
    assert body["total"] == 25
    assert body["pages"] == 3


def test_page_size_is_capped(shop):
    assert shop.client.get("/products", params={"size": 500}).status_code == 422
    assert shop.client.get("/products", params={"page": 0}).status_code == 422


def test_get_product(shop):
    product_id = shop.add_product("Mug", price_cents=1400)
    res = shop.client.get(f"/products/{product_id}")
    assert res.status_code == 200
    assert res.json()["price_cents"] == 1400


def test_unpublished_product_is_not_found(shop):
    product_id = shop.add_product("Secret", published=False)
    assert shop.client.get(f"/products/{product_id}").status_code == 404


def test_admin_creates_and_publishes_a_product(shop):
    headers = shop.admin()
    res = shop.client.post(
        "/admin/products",
        json={"name": "Teapot", "category": "kitchen", "price_cents": 3200, "stock": 5},
        headers=headers,
    )
    assert res.status_code == 201
    product = res.json()
    assert product["published"] is False

    res = shop.client.patch(f"/admin/products/{product['id']}", json={"published": True}, headers=headers)
    assert res.json()["published"] is True
    assert shop.client.get(f"/products/{product['id']}").status_code == 200


def test_admin_updates_price(shop):
    headers = shop.admin()
    product_id = shop.add_product("Mug", price_cents=1200)
    res = shop.client.patch(f"/admin/products/{product_id}", json={"price_cents": 1400}, headers=headers)
    assert res.status_code == 200
    assert res.json()["price_cents"] == 1400


def test_customers_cannot_manage_products(shop):
    headers = shop.customer()
    res = shop.client.post(
        "/admin/products",
        json={"name": "Teapot", "category": "kitchen", "price_cents": 3200, "stock": 5},
        headers=headers,
    )
    assert res.status_code == 403
