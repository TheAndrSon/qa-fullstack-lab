def login(client, email="alice@example.com", password="User123!"):
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products_list(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 10
    assert len(data["items"]) > 0
    assert {"id", "title", "price", "category", "stock"} <= set(data["items"][0])


def test_product_detail_and_404(client):
    response = client.get("/api/products/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    missing = client.get("/api/products/99999")
    assert missing.status_code == 404


def test_register_login_me_logout(client):
    register = client.post(
        "/api/register",
        json={
            "email": "new.user@example.com",
            "password": "Secret123!",
            "name": "New User",
        },
    )
    assert register.status_code == 201, register.text

    me = client.get("/api/me")
    assert me.status_code == 401

    login(client, "new.user@example.com", "Secret123!")
    me = client.get("/api/me")
    assert me.status_code == 200
    assert me.json()["email"] == "new.user@example.com"

    assert client.post("/api/logout").status_code == 200
    assert client.get("/api/me").status_code == 401


def test_login_with_wrong_password(client):
    response = client.post(
        "/api/login", json={"email": "alice@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_cart_checkout_and_orders(client):
    login(client)
    add = client.post("/api/cart", json={"product_id": 1, "qty": 2})
    assert add.status_code == 200
    assert add.json()["items"][0]["qty"] == 2

    cart = client.get("/api/cart")
    assert cart.status_code == 200
    assert cart.json()["total"] > 0

    checkout = client.post("/api/checkout")
    assert checkout.status_code == 201
    order_id = checkout.json()["id"]

    assert client.get("/api/cart").json()["items"] == []

    orders = client.get("/api/orders")
    assert orders.status_code == 200
    assert any(order["id"] == order_id for order in orders.json()["items"])

    detail = client.get(f"/api/orders/{order_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == order_id
    assert len(detail.json()["items"]) == 1


def test_admin_api_forbidden_for_regular_user(client):
    login(client)
    response = client.post("/api/admin/products", json={"title": "Hack", "price": 1})
    assert response.status_code == 403


def test_admin_can_create_product(client):
    login(client, "admin@shopsphere.local", "Admin123!")
    response = client.post(
        "/api/admin/products",
        json={
            "title": "QA Test Product",
            "price": 12.5,
            "category": "Test",
            "stock": 3,
            "emoji": "🧪",
        },
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    product = client.get(f"/api/products/{product_id}")
    assert product.status_code == 200
    assert product.json()["title"] == "QA Test Product"


def test_search_with_exact_case(client):
    response = client.get("/api/products", params={"q": "Aurora"})
    assert response.status_code == 200
    assert any("Aurora" in item["title"] for item in response.json()["items"])


def test_pages_render(client):
    for path in ["/", "/product/1", "/cart", "/login", "/register"]:
        response = client.get(path)
        assert response.status_code == 200, f"{path}: {response.text[:200]}"

    login(client, "admin@shopsphere.local", "Admin123!")
    admin = client.get("/admin")
    assert admin.status_code == 200
    assert "Админка" in admin.text


def test_filter_by_category(client):
    response = client.get("/api/products", params={"category": "Audio"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["category"] == "Audio" for item in items)
