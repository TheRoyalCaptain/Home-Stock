import csv
import io
import json
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)
DATA_DIR = Path(os.environ.get("HOME_STOCK_DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "home-stock.db"


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT NOT NULL DEFAULT 'stuks',
                minimum REAL NOT NULL DEFAULT 0,
                location TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '',
                barcode TEXT NOT NULL DEFAULT '',
                expiry_date TEXT,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS shopping_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1,
                unit TEXT NOT NULL DEFAULT 'stuks',
                checked INTEGER NOT NULL DEFAULT 0,
                product_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
            );
            """
        )


def product_from_payload(payload, current=None):
    def value(key, default=""):
        return payload.get(key, current[key] if current is not None else default)

    name = str(value("name")).strip()
    if not name:
        raise ValueError("Naam is verplicht")
    expiry = str(value("expiry_date", "") or "").strip() or None
    if expiry:
        date.fromisoformat(expiry)
    return {
        "name": name,
        "quantity": max(0, float(value("quantity", 0))),
        "unit": str(value("unit", "stuks")).strip() or "stuks",
        "minimum": max(0, float(value("minimum", 0))),
        "location": str(value("location", "")).strip(),
        "category": str(value("category", "")).strip(),
        "barcode": str(value("barcode", "")).strip(),
        "expiry_date": expiry,
        "notes": str(value("notes", "")).strip(),
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/products")
def list_products():
    search = request.args.get("search", "").strip()
    sql = "SELECT * FROM products"
    values = []
    if search:
        sql += " WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ? OR location LIKE ?"
        wildcard = f"%{search}%"
        values = [wildcard] * 4
    sql += " ORDER BY name COLLATE NOCASE"
    with db() as connection:
        return jsonify([dict(row) for row in connection.execute(sql, values)])


@app.post("/api/products")
def create_product():
    try:
        product = product_from_payload(request.get_json(force=True))
    except (ValueError, TypeError) as error:
        return jsonify(error=str(error)), 400
    columns = ", ".join(product)
    placeholders = ", ".join("?" for _ in product)
    with db() as connection:
        cursor = connection.execute(
            f"INSERT INTO products ({columns}) VALUES ({placeholders})", tuple(product.values())
        )
        row = connection.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.put("/api/products/<int:product_id>")
def update_product(product_id):
    with db() as connection:
        current = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if current is None:
            return jsonify(error="Product niet gevonden"), 404
        try:
            product = product_from_payload(request.get_json(force=True), current)
        except (ValueError, TypeError) as error:
            return jsonify(error=str(error)), 400
        assignments = ", ".join(f"{key} = ?" for key in product)
        connection.execute(
            f"UPDATE products SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (*product.values(), product_id),
        )
        row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return jsonify(dict(row))


@app.patch("/api/products/<int:product_id>/quantity")
def adjust_quantity(product_id):
    try:
        amount = float(request.get_json(force=True).get("amount", 0))
    except (ValueError, TypeError):
        return jsonify(error="Ongeldige hoeveelheid"), 400
    with db() as connection:
        connection.execute(
            "UPDATE products SET quantity = MAX(0, quantity + ?), updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (amount, product_id),
        )
        row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        return jsonify(error="Product niet gevonden"), 404
    return jsonify(dict(row))


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    with db() as connection:
        connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
    return "", 204


@app.get("/api/dashboard")
def dashboard():
    today = date.today()
    soon = today + timedelta(days=7)
    with db() as connection:
        total = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        low = connection.execute("SELECT COUNT(*) FROM products WHERE quantity <= minimum").fetchone()[0]
        expiring = connection.execute(
            "SELECT COUNT(*) FROM products WHERE expiry_date IS NOT NULL AND expiry_date <= ?",
            (soon.isoformat(),),
        ).fetchone()[0]
        locations = connection.execute(
            "SELECT COUNT(DISTINCT location) FROM products WHERE location <> ''"
        ).fetchone()[0]
    return jsonify(total=total, low=low, expiring=expiring, locations=locations)


@app.get("/api/shopping")
def shopping_list():
    with db() as connection:
        manual = [dict(row) for row in connection.execute("SELECT * FROM shopping_items ORDER BY checked, name")]
        automatic = [
            dict(row)
            for row in connection.execute(
                """SELECT id AS product_id, name, MAX(minimum - quantity, 1) AS quantity, unit,
                          0 AS checked, 1 AS automatic
                   FROM products WHERE quantity <= minimum ORDER BY name"""
            )
        ]
    return jsonify(automatic + manual)


@app.post("/api/shopping")
def add_shopping_item():
    payload = request.get_json(force=True)
    name = str(payload.get("name", "")).strip()
    if not name:
        return jsonify(error="Naam is verplicht"), 400
    try:
        quantity = max(0.01, float(payload.get("quantity", 1)))
    except (ValueError, TypeError):
        return jsonify(error="Ongeldige hoeveelheid"), 400
    unit = str(payload.get("unit", "stuks")).strip() or "stuks"
    with db() as connection:
        cursor = connection.execute(
            "INSERT INTO shopping_items (name, quantity, unit) VALUES (?, ?, ?)",
            (name, quantity, unit),
        )
        row = connection.execute("SELECT * FROM shopping_items WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.patch("/api/shopping/<int:item_id>")
def toggle_shopping_item(item_id):
    checked = 1 if request.get_json(force=True).get("checked") else 0
    with db() as connection:
        connection.execute("UPDATE shopping_items SET checked = ? WHERE id = ?", (checked, item_id))
    return "", 204


@app.delete("/api/shopping/<int:item_id>")
def delete_shopping_item(item_id):
    with db() as connection:
        connection.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
    return "", 204


@app.get("/api/export.csv")
def export_csv():
    output = io.StringIO()
    fields = ["name", "quantity", "unit", "minimum", "location", "category", "barcode", "expiry_date", "notes"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    with db() as connection:
        for row in connection.execute("SELECT * FROM products ORDER BY name"):
            writer.writerow({field: row[field] for field in fields})
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=home-stock.csv"},
    )


@app.get("/api/backup.json")
def backup_json():
    with db() as connection:
        payload = {
            "version": 1,
            "created": date.today().isoformat(),
            "products": [dict(row) for row in connection.execute("SELECT * FROM products")],
            "shopping_items": [dict(row) for row in connection.execute("SELECT * FROM shopping_items")],
        }
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=home-stock-backup.json"},
    )


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
