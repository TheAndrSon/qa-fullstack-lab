import hashlib
import os
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "data" / "shopsphere.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL,
    category TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    emoji TEXT NOT NULL DEFAULT '📦'
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
"""


def db_path() -> Path:
    path = Path(os.environ.get("SHOP_DB", str(DEFAULT_DB)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count == 0:
            seed(conn)
        conn.commit()


def seed(conn: sqlite3.Connection) -> None:
    users = [
        ("admin@shopsphere.local", "Admin123!", "Admin", "admin"),
        ("alice@example.com", "User123!", "Alice", "user"),
        ("bob@example.com", "User123!", "Bob", "user"),
    ]
    for email, password, name, role in users:
        salt = secrets.token_hex(8)
        conn.execute(
            "INSERT INTO users(email, password_hash, salt, name, role) VALUES (?, ?, ?, ?, ?)",
            (email, hash_password(password, salt), salt, name, role),
        )

    products = [
        (
            "Aurora Headphones",
            "Wireless over-ear headphones with active noise cancelling.",
            129.99,
            "Audio",
            12,
            "🎧",
        ),
        (
            "Nova Mechanical Keyboard",
            "Hot-swappable 75% keyboard with tactile switches.",
            89.50,
            "Accessories",
            20,
            "⌨️",
        ),
        (
            "Pulse Mouse",
            "Lightweight gaming mouse, 26k DPI sensor.",
            39.90,
            "Accessories",
            30,
            "🖱️",
        ),
        (
            "Orbit 27 Monitor",
            "27-inch QHD IPS monitor, 165 Hz.",
            249.00,
            "Displays",
            8,
            "🖥️",
        ),
        (
            "Flux USB-C Hub",
            "7-in-1 hub with HDMI, USB 3.0 and SD reader.",
            59.00,
            "Accessories",
            15,
            "🔌",
        ),
        (
            "Echo Speaker",
            "Compact Bluetooth speaker with deep bass.",
            79.00,
            "Audio",
            10,
            "🔊",
        ),
        (
            "Vertex Laptop Stand",
            "Aluminium stand with adjustable height.",
            34.50,
            "Accessories",
            25,
            "💻",
        ),
        (
            "Lumen Desk Lamp",
            "Warm-to-cool LED lamp with touch control.",
            44.00,
            "Home",
            18,
            "💡",
        ),
        (
            "Cable Kit Pro",
            "Braided USB-C, HDMI and audio cables.",
            19.90,
            "Accessories",
            50,
            "🧰",
        ),
        (
            "Shield Webcam",
            "1080p webcam with privacy shutter.",
            69.00,
            "Video",
            9,
            "📷",
        ),
    ]
    conn.executemany(
        "INSERT INTO products(title, description, price, category, stock, emoji) VALUES (?, ?, ?, ?, ?, ?)",
        products,
    )
