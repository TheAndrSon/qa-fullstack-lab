from __future__ import annotations

import math
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .db import connect, hash_password, init_db

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="ShopSphere", version="1.0.0")
app.add_middleware(
    SessionMiddleware, secret_key="shopsphere-dev-secret", session_cookie="shop_session"
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def _startup() -> None:
    init_db()


def as_dict(row) -> dict | None:
    return dict(row) if row else None


def current_user(request: Request) -> dict | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    with closing(connect()) as conn:
        return as_dict(
            conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        )


def require_user(request: Request) -> dict:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="login required")
    return user


def require_admin(request: Request) -> dict:
    user = require_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user


def get_cart(request: Request) -> dict:
    return request.session.setdefault("cart", {})


def save_cart(request: Request, cart: dict) -> None:
    request.session["cart"] = cart


def cart_items(request: Request) -> list[dict]:
    cart = get_cart(request)
    if not cart:
        return []
    ids = [int(key) for key in cart.keys()]
    placeholders = ",".join("?" for _ in ids)
    with closing(connect()) as conn:
        rows = conn.execute(
            f"SELECT * FROM products WHERE id IN ({placeholders})", ids
        ).fetchall()
    by_id = {row["id"]: as_dict(row) for row in rows}
    items: list[dict] = []
    for key, qty in cart.items():
        product = by_id.get(int(key))
        if not product:
            continue
        items.append(
            {**product, "qty": qty, "line_total": round(product["price"] * qty, 2)}
        )
    return items


def cart_total(items: list[dict]) -> float:
    return round(sum(item["line_total"] for item in items), 2)


def page_context(request: Request, **extra) -> dict:
    return {"request": request, "user": current_user(request), **extra}


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "shopsphere"})


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request, q: str = "", category: str = "", page: int = 1
) -> HTMLResponse:
    per_page = 4
    where: list[str] = []
    params: list = []
    if q:
        # BUG: GLOB is case-sensitive; search for "aurora" misses "Aurora".
        where.append("title GLOB ?")
        params.append(f"*{q}*")
    if category:
        where.append("category = ?")
        params.append(category)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with closing(connect()) as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM products {where_sql}", params
        ).fetchone()["c"]
        pages = max(1, math.ceil(total / per_page))
        page = max(1, min(page, pages))
        products = conn.execute(
            f"SELECT * FROM products {where_sql} ORDER BY id LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page],
        ).fetchall()
        categories = [
            row["category"]
            for row in conn.execute(
                "SELECT DISTINCT category FROM products ORDER BY category"
            )
        ]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=page_context(
            request,
            products=[as_dict(row) for row in products],
            categories=categories,
            q=q,
            category=category,
            page=page,
            pages=pages,
            total=total,
        ),
    )


@app.get("/product/{product_id}", response_class=HTMLResponse)
def product_page(request: Request, product_id: int) -> HTMLResponse:
    with closing(connect()) as conn:
        product = as_dict(
            conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
        )
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context=page_context(request, product=product),
    )


@app.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request) -> HTMLResponse:
    items = cart_items(request)
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context=page_context(request, items=items, total=cart_total(items)),
    )


@app.post("/cart/add")
def cart_add(
    request: Request, product_id: int = Form(...), qty: int = Form(1)
) -> RedirectResponse:
    # BUG: qty is not validated; negative and zero values are accepted.
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    save_cart(request, cart)
    return RedirectResponse(url="/cart", status_code=303)


@app.post("/cart/update")
def cart_update(
    request: Request, product_id: int = Form(...), qty: int = Form(...)
) -> RedirectResponse:
    # BUG: negative quantities are accepted and reduce the total.
    cart = get_cart(request)
    key = str(product_id)
    if qty == 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    save_cart(request, cart)
    return RedirectResponse(url="/cart", status_code=303)


@app.post("/cart/remove")
def cart_remove(request: Request, product_id: int = Form(...)) -> RedirectResponse:
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    return RedirectResponse(url="/cart", status_code=303)


@app.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request) -> HTMLResponse:
    items = cart_items(request)
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context=page_context(request, items=items, total=cart_total(items)),
    )


@app.post("/checkout")
def checkout(request: Request) -> RedirectResponse:
    user = current_user(request)
    if not user:
        return RedirectResponse(
            url="/login?error=Войдите, чтобы оформить заказ", status_code=303
        )
    items = cart_items(request)
    if not items:
        return RedirectResponse(url="/cart", status_code=303)
    total = cart_total(items)
    with closing(connect()) as conn:
        cursor = conn.execute(
            "INSERT INTO orders(user_id, total, status) VALUES (?, ?, ?)",
            (user["id"], total, "created"),
        )
        order_id = cursor.lastrowid
        for item in items:
            # BUG: stock is not checked or decremented.
            conn.execute(
                "INSERT INTO order_items(order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, item["id"], item["qty"], item["price"]),
            )
        conn.commit()
    request.session["cart"] = {}
    return RedirectResponse(url=f"/orders/{order_id}", status_code=303)


@app.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request) -> HTMLResponse:
    user = current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=Войдите", status_code=303)
    with closing(connect()) as conn:
        orders = conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user["id"],)
        ).fetchall()
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context=page_context(request, orders=[as_dict(row) for row in orders]),
    )


@app.get("/orders/{order_id}", response_class=HTMLResponse)
def order_page(request: Request, order_id: int) -> HTMLResponse:
    # BUG: no ownership check. Any logged-in (or even anonymous) user can open any order.
    with closing(connect()) as conn:
        order = as_dict(
            conn.execute(
                "SELECT o.*, u.email AS user_email FROM orders o JOIN users u ON u.id = o.user_id WHERE o.id = ?",
                (order_id,),
            ).fetchone()
        )
        items = conn.execute(
            "SELECT oi.*, p.title, p.emoji FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE oi.order_id = ?",
            (order_id,),
        ).fetchall()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return templates.TemplateResponse(
        request=request,
        name="order.html",
        context=page_context(
            request, order=order, items=[as_dict(row) for row in items]
        ),
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request) -> HTMLResponse:
    # BUG: role is not checked on GET; a regular user can open the admin page.
    if not current_user(request):
        return RedirectResponse(url="/login?error=Войдите", status_code=303)
    with closing(connect()) as conn:
        products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context=page_context(request, products=[as_dict(row) for row in products]),
    )


@app.post("/admin/products")
def admin_create_product(
    request: Request,
    title: str = Form(...),
    price: float = Form(...),
    category: str = Form("Accessories"),
    stock: int = Form(0),
    emoji: str = Form("📦"),
    description: str = Form(""),
) -> RedirectResponse:
    require_admin(request)
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO products(title, description, price, category, stock, emoji) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, price, category, stock, emoji),
        )
        conn.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/products/{product_id}/delete")
def admin_delete_product(request: Request, product_id: int) -> RedirectResponse:
    require_admin(request)
    with closing(connect()) as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="login.html", context=page_context(request)
    )


@app.post("/login")
def login(
    request: Request, email: str = Form(...), password: str = Form(...)
) -> RedirectResponse:
    with closing(connect()) as conn:
        user = as_dict(
            conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        )
    if not user or hash_password(password, user["salt"]) != user["password_hash"]:
        return RedirectResponse(
            url="/login?error=Неверный email или пароль", status_code=303
        )
    request.session["user_id"] = user["id"]
    return RedirectResponse(url="/", status_code=303)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="register.html", context=page_context(request)
    )


@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(""),
) -> RedirectResponse:
    with closing(connect()) as conn:
        # BUG: duplicate check is case-sensitive, so Alice@Example.com and alice@example.com coexist.
        exists = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if exists:
            return RedirectResponse(
                url="/register?error=Этот email уже занят", status_code=303
            )
        salt = __import__("secrets").token_hex(8)
        conn.execute(
            "INSERT INTO users(email, password_hash, salt, name, role) VALUES (?, ?, ?, ?, 'user')",
            (email, hash_password(password, salt), salt, name or email.split("@")[0]),
        )
        conn.commit()
    return RedirectResponse(url="/login?msg=Аккаунт создан, войдите", status_code=303)


@app.get("/logout")
def logout(request: Request) -> RedirectResponse:
    # BUG: cart is not cleared on logout.
    request.session.pop("user_id", None)
    return RedirectResponse(url="/", status_code=303)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


@app.post("/api/register")
async def api_register(request: Request) -> JSONResponse:
    payload = await request.json()
    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", ""))
    name = str(payload.get("name", "")) or email.split("@")[0]
    if not email or len(password) < 6:
        return JSONResponse(
            {"error": "email and password (6+) are required"}, status_code=400
        )
    with closing(connect()) as conn:
        exists = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if exists:
            return JSONResponse({"error": "email already exists"}, status_code=409)
        salt = __import__("secrets").token_hex(8)
        cursor = conn.execute(
            "INSERT INTO users(email, password_hash, salt, name, role) VALUES (?, ?, ?, ?, 'user')",
            (email, hash_password(password, salt), salt, name),
        )
        conn.commit()
        user_id = cursor.lastrowid
    return JSONResponse(
        {"id": user_id, "email": email, "name": name, "role": "user"}, status_code=201
    )


@app.post("/api/login")
async def api_login(request: Request) -> JSONResponse:
    payload = await request.json()
    email = str(payload.get("email", ""))
    password = str(payload.get("password", ""))
    with closing(connect()) as conn:
        user = as_dict(
            conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        )
    if not user or hash_password(password, user["salt"]) != user["password_hash"]:
        return JSONResponse({"error": "invalid credentials"}, status_code=401)
    request.session["user_id"] = user["id"]
    return JSONResponse(
        {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    )


@app.post("/api/logout")
def api_logout(request: Request) -> JSONResponse:
    # BUG: cart is not cleared on logout.
    request.session.pop("user_id", None)
    return JSONResponse({"ok": True})


@app.get("/api/me")
def api_me(request: Request) -> JSONResponse:
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "login required"}, status_code=401)
    return JSONResponse(
        {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    )


@app.get("/api/products")
def api_products(
    request: Request, q: str = "", category: str = "", page: int = 1, per_page: int = 10
) -> JSONResponse:
    where: list[str] = []
    params: list = []
    if q:
        # BUG: case-sensitive GLOB.
        where.append("title GLOB ?")
        params.append(f"*{q}*")
    if category:
        where.append("category = ?")
        params.append(category)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    per_page = max(1, min(per_page, 50))
    with closing(connect()) as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM products {where_sql}", params
        ).fetchone()["c"]
        pages = max(1, math.ceil(total / per_page))
        page = max(1, min(page, pages))
        rows = conn.execute(
            f"SELECT * FROM products {where_sql} ORDER BY id LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page],
        ).fetchall()
    return JSONResponse(
        {
            "items": [as_dict(row) for row in rows],
            "total": total,
            "page": page,
            "pages": pages,
            "per_page": per_page,
        }
    )


@app.get("/api/products/{product_id}")
def api_product(product_id: int) -> JSONResponse:
    with closing(connect()) as conn:
        product = as_dict(
            conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
        )
    if not product:
        return JSONResponse({"error": "product not found"}, status_code=404)
    return JSONResponse(product)


@app.get("/api/cart")
def api_cart(request: Request) -> JSONResponse:
    items = cart_items(request)
    return JSONResponse({"items": items, "total": cart_total(items)})


@app.post("/api/cart")
async def api_cart_add(request: Request) -> JSONResponse:
    payload = await request.json()
    product_id = int(payload.get("product_id", 0))
    qty = int(payload.get("qty", 1))
    # BUG: qty is not validated (negative/zero allowed).
    with closing(connect()) as conn:
        product = conn.execute(
            "SELECT id FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    if not product:
        return JSONResponse({"error": "product not found"}, status_code=404)
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    save_cart(request, cart)
    items = cart_items(request)
    return JSONResponse({"items": items, "total": cart_total(items)})


@app.post("/api/checkout")
def api_checkout(request: Request) -> JSONResponse:
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "login required"}, status_code=401)
    items = cart_items(request)
    if not items:
        return JSONResponse({"error": "cart is empty"}, status_code=400)
    total = cart_total(items)
    with closing(connect()) as conn:
        cursor = conn.execute(
            "INSERT INTO orders(user_id, total, status) VALUES (?, ?, ?)",
            (user["id"], total, "created"),
        )
        order_id = cursor.lastrowid
        for item in items:
            # BUG: stock is not checked or decremented.
            conn.execute(
                "INSERT INTO order_items(order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, item["id"], item["qty"], item["price"]),
            )
        conn.commit()
    request.session["cart"] = {}
    return JSONResponse(
        {"id": order_id, "total": total, "status": "created"}, status_code=201
    )


@app.get("/api/orders")
def api_orders(request: Request) -> JSONResponse:
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "login required"}, status_code=401)
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user["id"],)
        ).fetchall()
    return JSONResponse({"items": [as_dict(row) for row in rows]})


@app.get("/api/orders/{order_id}")
def api_order(request: Request, order_id: int) -> JSONResponse:
    # BUG: IDOR — no ownership check.
    with closing(connect()) as conn:
        order = as_dict(
            conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        )
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()
    if not order:
        return JSONResponse({"error": "order not found"}, status_code=404)
    return JSONResponse({**order, "items": [as_dict(row) for row in items]})


@app.post("/api/admin/products")
async def api_admin_create(request: Request) -> JSONResponse:
    require_admin(request)
    payload = await request.json()
    with closing(connect()) as conn:
        cursor = conn.execute(
            "INSERT INTO products(title, description, price, category, stock, emoji) VALUES (?, ?, ?, ?, ?, ?)",
            (
                payload.get("title", "Untitled"),
                payload.get("description", ""),
                float(payload.get("price", 0)),
                payload.get("category", "Accessories"),
                int(payload.get("stock", 0)),
                payload.get("emoji", "📦"),
            ),
        )
        conn.commit()
        product_id = cursor.lastrowid
    return JSONResponse({"id": product_id}, status_code=201)


@app.delete("/api/admin/products/{product_id}")
def api_admin_delete(request: Request, product_id: int) -> JSONResponse:
    require_admin(request)
    with closing(connect()) as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    return JSONResponse({"ok": True})
