def test_login_returns_a_token_that_works(shop):
    headers = shop.customer("alice@example.com")
    res = shop.client.get("/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "alice@example.com"


def test_login_is_case_insensitive_on_email(shop):
    shop.add_user("alice@example.com")
    res = shop.client.post("/auth/login", json={"email": "Alice@Example.com", "password": shop.password})
    assert res.status_code == 200


def test_wrong_password_is_rejected(shop):
    shop.add_user("alice@example.com")
    res = shop.client.post("/auth/login", json={"email": "alice@example.com", "password": "nope"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"


def test_unknown_email_gets_the_same_error(shop):
    res = shop.client.post("/auth/login", json={"email": "ghost@example.com", "password": shop.password})
    assert res.status_code == 401


def test_missing_token(shop):
    assert shop.client.get("/auth/me").status_code == 401


def test_session_expires_after_a_week(shop):
    headers = shop.customer()
    shop.clock.advance(days=7, seconds=1)
    assert shop.client.get("/auth/me", headers=headers).status_code == 401
