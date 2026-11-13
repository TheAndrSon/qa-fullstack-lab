"""Known bugs: tests assert the EXPECTED behavior and are expected to fail.

They are marked xfail(strict=True), so CI stays green while the bugs exist.
When a bug is fixed, the test will XPASS and fail the suite — remove the marker then.
"""

import pytest


def login(client, email="alice@example.com", password="User123!"):
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text


@pytest.mark.xfail(strict=True, reason="BUG-01: negative cart quantity is accepted")
def test_negative_cart_quantity_is_rejected(client):
    login(client)
    response = client.post("/api/cart", json={"product_id": 1, "qty": -5})
    assert response.status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-02: search is case-sensitive")
def test_search_is_case_insensitive(client):
    response = client.get("/api/products", params={"q": "aurora"})
    assert response.status_code == 200
    assert any("Aurora" in item["title"] for item in response.json()["items"])


@pytest.mark.xfail(strict=True, reason="BUG-03: any user can read any order (IDOR)")
def test_order_isolation_between_users(client):
    login(client)
    client.post("/api/cart", json={"product_id": 2, "qty": 1})
    order_id = client.post("/api/checkout").json()["id"]
    client.post("/api/logout")

    login(client, "bob@example.com", "User123!")
    response = client.get(f"/api/orders/{order_id}")
    assert response.status_code in (403, 404)


@pytest.mark.xfail(
    strict=True, reason="BUG-04: duplicate email check is case-sensitive"
)
def test_duplicate_email_in_different_case_is_rejected(client):
    response = client.post(
        "/api/register",
        json={
            "email": "Alice@Example.com",
            "password": "Secret123!",
            "name": "Alice Clone",
        },
    )
    assert response.status_code in (400, 409)


@pytest.mark.xfail(
    strict=True, reason="BUG-05: cart survives logout and leaks to the next user"
)
def test_logout_clears_cart(client):
    login(client)
    client.post("/api/cart", json={"product_id": 3, "qty": 1})
    client.post("/api/logout")
    login(client, "bob@example.com", "User123!")
    assert client.get("/api/cart").json()["items"] == []


@pytest.mark.xfail(
    strict=True, reason="BUG-06: admin page is available to any logged-in user"
)
def test_admin_page_forbidden_for_regular_user(client):
    login(client)
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 403


@pytest.mark.xfail(strict=True, reason="BUG-07: stock is not checked at checkout")
def test_checkout_rejects_quantity_above_stock(client):
    login(client)
    client.post("/api/cart", json={"product_id": 1, "qty": 999})
    response = client.post("/api/checkout")
    assert response.status_code == 400
