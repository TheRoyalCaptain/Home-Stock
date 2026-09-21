import csv
import hashlib
import io
import json
import os
import re
import secrets
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

from barcode import Code128
from barcode.writer import SVGWriter
from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)
DATA_DIR = Path(os.environ.get("HOME_STOCK_DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "home-stock.db"
APP_VERSION = "0.2.1"
USER_AGENT = "HomeStock/0.2 (https://github.com/TheRoyalCaptain/Home-Stock)"


def db():
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def table_columns(connection, table):
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def add_column(connection, table, definition):
    if definition.split()[0] not in table_columns(connection, table):
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def unique_code(connection):
    while True:
        code = "HS-" + secrets.token_hex(3).upper()
        if not connection.execute("SELECT 1 FROM stock_lots WHERE lot_code=?", (code,)).fetchone():
            return code


def setting(connection, key, default=""):
    row = connection.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def body():
    return request.get_json(silent=True) or {}


def number(value, default=0, minimum=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = float(default)
    return max(minimum, result) if minimum is not None else result


def iso_date(value):
    return date.fromisoformat(str(value)).isoformat() if value else None


def actor(payload=None):
    payload = payload or {}
    return int(payload.get("profile_id") or request.headers.get("X-Profile-Id") or 1)


def product_query():
    return """
      SELECT p.*, COALESCE(SUM(l.quantity),0) stock,
        MIN(CASE WHEN l.quantity>0 THEN l.expiry_date END) next_expiry,
        COUNT(DISTINCT CASE WHEN l.quantity>0 THEN l.id END) lot_count,
        GROUP_CONCAT(DISTINCT CASE WHEN l.quantity>0 THEN loc.name END) locations,
        GROUP_CONCAT(DISTINCT b.barcode) barcodes
      FROM products p
      LEFT JOIN stock_lots l ON l.product_id=p.id
      LEFT JOIN locations loc ON loc.id=l.location_id
      LEFT JOIN barcodes b ON b.product_id=p.id
    """


def seed_rules(connection):
    rules = [
        ("melk", "zuivel", "fridge", 7, 3), ("yoghurt", "zuivel", "fridge", 14, 5),
        ("kaas", "zuivel", "fridge", 21, 10), ("boter", "zuivel", "fridge", 30, 21),
        ("ei", "eieren", "fridge", 28, 7), ("kip", "vlees", "fridge", 2, 1),
        ("rund", "vlees", "fridge", 3, 1), ("gehakt", "vlees", "fridge", 2, 1),
        ("vis", "vis", "fridge", 2, 1), ("brood", "bakkerij", "pantry", 4, 3),
        ("groente", "groente", "fridge", 7, 4), ("sla", "groente", "fridge", 5, 2),
        ("tomaat", "groente", "pantry", 7, 4), ("fruit", "fruit", "fridge", 7, 4),
        ("appel", "fruit", "fridge", 21, 10), ("banaan", "fruit", "pantry", 5, 2),
        ("restje", "bereid", "fridge", 3, 2), ("maaltijd", "bereid", "fridge", 3, 2),
        ("", "", "freezer", 90, 60), ("blik", "conserven", "pantry", 730, 365),
        ("pasta", "droog", "pantry", 730, 365), ("rijst", "droog", "pantry", 730, 365),
        ("saus", "sauzen", "pantry", 365, 7), ("sap", "dranken", "fridge", 14, 5),
    ]
    connection.executemany(
        """INSERT OR IGNORE INTO shelf_life_rules
        (name_pattern,category,location_kind,unopened_days,opened_days)
        VALUES (?,?,?,?,?)""", rules
    )


def migrate_v1(connection):
    if connection.execute("SELECT COUNT(*) FROM stock_lots").fetchone()[0]:
        return
    for product in connection.execute("SELECT * FROM products WHERE quantity>0").fetchall():
        location_name = product["location"] or "Voorraadkast"
        loc = connection.execute(
            "SELECT id FROM locations WHERE name=? COLLATE NOCASE", (location_name,)
        ).fetchone()
        if not loc:
            loc_id = connection.execute(
                "INSERT INTO locations(name,kind,emoji) VALUES(?,'custom','📦')", (location_name,)
            ).lastrowid
        else:
            loc_id = loc["id"]
        code = unique_code(connection)
        lot_id = connection.execute(
            """INSERT INTO stock_lots
            (product_id,location_id,quantity,unit,expiry_date,lot_code,created_by)
            VALUES(?,?,?,?,?,?,1)""",
            (product["id"], loc_id, product["quantity"], product["unit"], product["expiry_date"], code),
        ).lastrowid
        connection.execute(
            """INSERT INTO stock_transactions
            (product_id,lot_id,profile_id,action,quantity,note)
            VALUES(?,?,1,'import',?,'Migratie vanuit v0.1')""",
            (product["id"], lot_id, product["quantity"]),
        )
        if product["barcode"]:
            connection.execute(
                "INSERT OR IGNORE INTO barcodes(product_id,barcode) VALUES(?,?)",
                (product["id"], product["barcode"]),
            )


def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS products(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,
          quantity REAL NOT NULL DEFAULT 0,unit TEXT NOT NULL DEFAULT 'stuks',
          minimum REAL NOT NULL DEFAULT 0,location TEXT NOT NULL DEFAULT '',
          category TEXT NOT NULL DEFAULT '',barcode TEXT NOT NULL DEFAULT '',
          expiry_date TEXT,notes TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS shopping_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,
          quantity REAL NOT NULL DEFAULT 1,unit TEXT NOT NULL DEFAULT 'stuks',
          checked INTEGER NOT NULL DEFAULT 0,product_id INTEGER,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS locations(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE COLLATE NOCASE,
          kind TEXT NOT NULL DEFAULT 'custom',emoji TEXT NOT NULL DEFAULT '📦',
          is_fixed INTEGER NOT NULL DEFAULT 0,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS profiles(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE COLLATE NOCASE,
          color TEXT NOT NULL DEFAULT '#14956f',avatar TEXT NOT NULL DEFAULT '👤',
          pin_hash TEXT,is_admin INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS stock_lots(
          id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER NOT NULL,
          location_id INTEGER NOT NULL,quantity REAL NOT NULL DEFAULT 0,
          unit TEXT NOT NULL DEFAULT 'stuks',purchase_date TEXT,expiry_date TEXT,
          opened_at TEXT,unit_price REAL,store TEXT NOT NULL DEFAULT '',
          lot_code TEXT NOT NULL UNIQUE,created_by INTEGER,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
          FOREIGN KEY(location_id) REFERENCES locations(id),
          FOREIGN KEY(created_by) REFERENCES profiles(id));
        CREATE TABLE IF NOT EXISTS barcodes(
          id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER NOT NULL,
          barcode TEXT NOT NULL UNIQUE,barcode_type TEXT NOT NULL DEFAULT 'retail',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS stock_transactions(
          id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER NOT NULL,lot_id INTEGER,
          profile_id INTEGER,action TEXT NOT NULL,quantity REAL NOT NULL DEFAULT 0,
          unit_price REAL,store TEXT NOT NULL DEFAULT '',note TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
          FOREIGN KEY(lot_id) REFERENCES stock_lots(id) ON DELETE SET NULL,
          FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS shelf_life_rules(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name_pattern TEXT NOT NULL DEFAULT '',
          category TEXT NOT NULL DEFAULT '',location_kind TEXT NOT NULL,
          unopened_days INTEGER NOT NULL,opened_days INTEGER,
          source TEXT NOT NULL DEFAULT 'built-in',use_count INTEGER NOT NULL DEFAULT 0,
          UNIQUE(name_pattern,category,location_kind));
        CREATE TABLE IF NOT EXISTS settings(
          key TEXT PRIMARY KEY,value TEXT NOT NULL,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS label_jobs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER NOT NULL,lot_id INTEGER,
          status TEXT NOT NULL DEFAULT 'queued',copies INTEGER NOT NULL DEFAULT 1,
          template TEXT NOT NULL DEFAULT 'compact',label_size TEXT NOT NULL DEFAULT '57x32',
          printed_at TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
          FOREIGN KEY(lot_id) REFERENCES stock_lots(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS notifications(
          id INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT NOT NULL,title TEXT NOT NULL,
          message TEXT NOT NULL,product_id INTEGER,lot_id INTEGER,due_at TEXT,
          is_read INTEGER NOT NULL DEFAULT 0,dedupe_key TEXT UNIQUE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
          FOREIGN KEY(lot_id) REFERENCES stock_lots(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS recipes(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,
          servings INTEGER NOT NULL DEFAULT 2,instructions TEXT NOT NULL DEFAULT '',
          prep_minutes INTEGER NOT NULL DEFAULT 0,emoji TEXT NOT NULL DEFAULT '🍽️',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS recipe_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,recipe_id INTEGER NOT NULL,product_id INTEGER,
          ingredient TEXT NOT NULL,amount REAL NOT NULL DEFAULT 1,
          unit TEXT NOT NULL DEFAULT 'stuks',
          FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
          FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS meal_plan(
          id INTEGER PRIMARY KEY AUTOINCREMENT,plan_date TEXT NOT NULL,
          meal TEXT NOT NULL DEFAULT 'avondeten',recipe_id INTEGER NOT NULL,
          servings INTEGER NOT NULL DEFAULT 2,note TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE);
        CREATE INDEX IF NOT EXISTS idx_lots_product ON stock_lots(product_id);
        CREATE INDEX IF NOT EXISTS idx_lots_expiry ON stock_lots(expiry_date);
        CREATE INDEX IF NOT EXISTS idx_tx_created ON stock_transactions(created_at);
        """)
        for definition in [
            "brand TEXT NOT NULL DEFAULT ''", "image_url TEXT NOT NULL DEFAULT ''",
            "default_shelf_days INTEGER", "opened_shelf_days INTEGER",
        ]:
            add_column(c, "products", definition)
        c.executemany(
            "INSERT OR IGNORE INTO locations(name,kind,emoji,is_fixed) VALUES(?,?,?,1)",
            [("Koelkast","fridge","🧊"),("Vriezer","freezer","❄️"),("Voorraadkast","pantry","🥫")],
        )
        c.execute("""INSERT OR IGNORE INTO profiles
          (id,name,color,avatar,is_admin) VALUES(1,'Kevin','#14956f','👤',1)""")
        defaults = {
            "gemini_model":"gemini-3.1-flash-lite","expiry_warning_days":"7",
            "label_size":"57x32","label_template":"compact","currency":"EUR",
        }
        c.executemany("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", defaults.items())
        seed_rules(c)
        migrate_v1(c)


def estimate_local(c, name, category, location_kind, opened=False):
    clean_name, clean_category = name.lower().strip(), category.lower().strip()
    rows = c.execute(
        """SELECT *,
          (CASE WHEN name_pattern<>'' AND instr(?,lower(name_pattern))>0 THEN 100 ELSE 0 END+
           CASE WHEN category<>'' AND lower(category)=? THEN 50 ELSE 0 END+
           CASE WHEN location_kind=? THEN 20 ELSE 0 END) score
          FROM shelf_life_rules WHERE location_kind=?
          ORDER BY score DESC,length(name_pattern) DESC""",
        (clean_name, clean_category, location_kind, location_kind),
    ).fetchall()
    rule = next((r for r in rows if r["score"]>=20 and
                 (r["name_pattern"] or r["category"] or location_kind=="freezer")), None)
    if not rule:
        return None
    days = rule["opened_days"] if opened and rule["opened_days"] else rule["unopened_days"]
    c.execute("UPDATE shelf_life_rules SET use_count=use_count+1 WHERE id=?", (rule["id"],))
    return {"days":days,"source":rule["source"],
            "confidence":"high" if rule["score"]>=70 else "medium"}


def estimate_gemini(c, name, category, location_name, opened=False):
    api_key = setting(c, "gemini_api_key")
    if not api_key:
        return None
    model = setting(c, "gemini_model", "gemini-3.1-flash-lite")
    prompt = (
        "Schat conservatief de voedselveilige houdbaarheid in dagen. "
        "Geef alleen JSON volgens schema. Product: %s. Categorie: %s. "
        "Bewaarlocatie: %s. Status: %s. Gebruik Nederlandse omstandigheden."
        % (name, category or "onbekend", location_name,
           "geopend" if opened else "ongeopend of vers bereid")
    )
    schema = {"type":"object","properties":{
        "days":{"type":"integer","minimum":1,"maximum":3650},
        "category":{"type":"string"},"storage_tip":{"type":"string"},
        "reason":{"type":"string"},
        "confidence":{"type":"string","enum":["low","medium","high"]}},
        "required":["days","category","storage_tip","reason","confidence"]}
    payload = {"contents":[{"parts":[{"text":prompt}]}],
               "generationConfig":{"responseMimeType":"application/json",
               "responseJsonSchema":schema,"maxOutputTokens":300}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model)}:generateContent",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","x-goog-api-key":api_key,
                 "User-Agent":USER_AGENT}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=18) as response:
            raw = json.load(response)
        result = json.loads(raw["candidates"][0]["content"]["parts"][0]["text"])
        result["source"] = "gemini"
        return result
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError,
            ValueError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Gemini kon geen inschatting maken: {error}") from error


def open_food_facts(barcode):
    fields = ("code,product_name,product_name_nl,brands,quantity,categories,"
              "categories_tags,image_front_small_url,nutriscore_grade")
    url = (f"https://world.openfoodfacts.org/api/v2/product/"
           f"{urllib.parse.quote(barcode)}.json?fields={fields}")
    req = urllib.request.Request(url, headers={"User-Agent":USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as error:
        raise RuntimeError(f"Open Food Facts is niet bereikbaar: {error}") from error
    if raw.get("status")!=1 or not raw.get("product"):
        return None
    p = raw["product"]
    return {
        "barcode":barcode,
        "name":p.get("product_name_nl") or p.get("product_name") or "Onbekend product",
        "brand":p.get("brands",""),"package_quantity":p.get("quantity",""),
        "category":(p.get("categories") or "").split(",")[0].strip(),
        "image_url":p.get("image_front_small_url",""),
        "nutriscore":p.get("nutriscore_grade",""),"source":"Open Food Facts"}


def refresh_notifications(c):
    today = date.today()
    warning = int(setting(c, "expiry_warning_days", "7"))
    soon = (today+timedelta(days=warning)).isoformat()
    lots = c.execute("""SELECT l.*,p.name FROM stock_lots l
      JOIN products p ON p.id=l.product_id
      WHERE l.quantity>0 AND l.expiry_date IS NOT NULL AND l.expiry_date<=?""",(soon,)).fetchall()
    for lot in lots:
        expired = lot["expiry_date"]<today.isoformat()
        c.execute("""INSERT OR IGNORE INTO notifications
          (type,title,message,product_id,lot_id,due_at,dedupe_key)
          VALUES(?,?,?,?,?,?,?)""",
          ("expired" if expired else "expiring",
           f"{lot['name']} is {'over datum' if expired else 'bijna over datum'}",
           f"Partij {lot['lot_code']} · {lot['expiry_date']}",
           lot["product_id"],lot["id"],lot["expiry_date"],
           f"expiry:{lot['id']}:{lot['expiry_date']}"))
    lows = c.execute(product_query()+"""
      GROUP BY p.id HAVING stock<=p.minimum AND p.minimum>0""").fetchall()
    for product in lows:
        c.execute("""INSERT OR IGNORE INTO notifications
          (type,title,message,product_id,due_at,dedupe_key)
          VALUES('low',?,?,?,?,?)""",
          (f"{product['name']} bijna op",f"Nog {product['stock']:g} {product['unit']}",
           product["id"],today.isoformat(),f"low:{product['id']}:{today.isoformat()}"))


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


@app.get("/api/bootstrap")
def bootstrap():
    with db() as c:
        refresh_notifications(c)
        locations=[dict(r) for r in c.execute("SELECT * FROM locations ORDER BY is_fixed DESC,name")]
        profiles=[dict(r) for r in c.execute(
            "SELECT id,name,color,avatar,is_admin,created_at FROM profiles ORDER BY id")]
        unread=c.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0").fetchone()[0]
        settings={r["key"]:r["value"] for r in c.execute("SELECT key,value FROM settings")
                  if r["key"]!="gemini_api_key"}
        settings["gemini_configured"]=bool(setting(c,"gemini_api_key"))
    return jsonify(version=APP_VERSION,locations=locations,profiles=profiles,
                   unread=unread,settings=settings)


@app.get("/api/products")
def products():
    search=request.args.get("search","").strip()
    sql=product_query(); values=[]
    if search:
        sql+=" WHERE p.name LIKE ? OR p.brand LIKE ? OR p.category LIKE ? OR b.barcode LIKE ? OR loc.name LIKE ?"
        values=[f"%{search}%"]*5
    sql+=" GROUP BY p.id ORDER BY p.name COLLATE NOCASE"
    with db() as c:
        return jsonify([dict(r) for r in c.execute(sql,values)])


@app.get("/api/products/<int:product_id>")
def product_detail(product_id):
    with db() as c:
        p=c.execute(product_query()+" WHERE p.id=? GROUP BY p.id",(product_id,)).fetchone()
        if not p:return jsonify(error="Product niet gevonden"),404
        lots=[dict(r) for r in c.execute("""SELECT l.*,loc.name location_name,
          loc.kind location_kind,pr.name profile_name FROM stock_lots l
          JOIN locations loc ON loc.id=l.location_id
          LEFT JOIN profiles pr ON pr.id=l.created_by WHERE l.product_id=?
          ORDER BY l.expiry_date IS NULL,l.expiry_date,l.created_at""",(product_id,))]
        history=[dict(r) for r in c.execute("""SELECT t.*,pr.name profile_name,l.lot_code
          FROM stock_transactions t LEFT JOIN profiles pr ON pr.id=t.profile_id
          LEFT JOIN stock_lots l ON l.id=t.lot_id WHERE t.product_id=?
          ORDER BY t.created_at DESC LIMIT 100""",(product_id,))]
    return jsonify(product=dict(p),lots=lots,history=history)


@app.post("/api/products")
def create_product():
    p=body(); name=str(p.get("name","")).strip()
    if not name:return jsonify(error="Naam is verplicht"),400
    quantity=number(p.get("quantity"),1,0)
    location_id=int(p.get("location_id") or 1)
    purchase=iso_date(p.get("purchase_date")) or date.today().isoformat()
    expiry=iso_date(p.get("expiry_date"))
    barcode=re.sub(r"\s+","",str(p.get("barcode","")))
    with db() as c:
        loc=c.execute("SELECT * FROM locations WHERE id=?",(location_id,)).fetchone()
        if not loc:return jsonify(error="Locatie niet gevonden"),400
        pid=c.execute("""INSERT INTO products
          (name,unit,minimum,category,barcode,notes,brand,image_url,
           default_shelf_days,opened_shelf_days) VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (name,str(p.get("unit") or "stuks"),number(p.get("minimum"),0,0),
           str(p.get("category") or ""),barcode,str(p.get("notes") or ""),
           str(p.get("brand") or ""),str(p.get("image_url") or ""),
           p.get("default_shelf_days") or None,p.get("opened_shelf_days") or None)).lastrowid
        if barcode:c.execute("INSERT INTO barcodes(product_id,barcode) VALUES(?,?)",(pid,barcode))
        lot_id=lot_code=None
        if quantity>0:
            lot_code=unique_code(c)
            lot_id=c.execute("""INSERT INTO stock_lots
              (product_id,location_id,quantity,unit,purchase_date,expiry_date,
               unit_price,store,lot_code,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (pid,location_id,quantity,str(p.get("unit") or "stuks"),purchase,expiry,
               number(p.get("unit_price"),0) or None,str(p.get("store") or ""),
               lot_code,actor(p))).lastrowid
            c.execute("""INSERT INTO stock_transactions
              (product_id,lot_id,profile_id,action,quantity,unit_price,store,note)
              VALUES(?,?,?,'purchase',?,?,?,'Product toegevoegd')""",
              (pid,lot_id,actor(p),quantity,number(p.get("unit_price"),0) or None,
               str(p.get("store") or "")))
        job_id=None
        if p.get("create_label") and lot_id:
            job_id=c.execute("""INSERT INTO label_jobs
              (product_id,lot_id,status,copies,template,label_size)
              VALUES(?,?,'preview',?,?,?)""",
              (pid,lot_id,int(p.get("label_copies") or 1),
               setting(c,"label_template","compact"),setting(c,"label_size","57x32"))).lastrowid
    return jsonify(id=pid,lot_id=lot_id,lot_code=lot_code,label_job_id=job_id),201


@app.put("/api/products/<int:product_id>")
def update_product(product_id):
    p=body(); allowed=["name","unit","minimum","category","notes","brand",
                      "image_url","default_shelf_days","opened_shelf_days"]
    fields={k:p[k] for k in allowed if k in p}
    if not fields:return jsonify(error="Geen wijzigingen"),400
    with db() as c:
        if not c.execute("SELECT 1 FROM products WHERE id=?",(product_id,)).fetchone():
            return jsonify(error="Product niet gevonden"),404
        c.execute("UPDATE products SET "+",".join(f"{k}=?" for k in fields)+
                  ",updated_at=CURRENT_TIMESTAMP WHERE id=?",
                  (*fields.values(),product_id))
    return jsonify(ok=True)


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    with db() as c:c.execute("DELETE FROM products WHERE id=?",(product_id,))
    return "",204


@app.post("/api/products/<int:product_id>/lots")
def add_lot(product_id):
    p=body(); quantity=number(p.get("quantity"),1,.01)
    with db() as c:
        product=c.execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone()
        if not product:return jsonify(error="Product niet gevonden"),404
        code=unique_code(c)
        lot_id=c.execute("""INSERT INTO stock_lots
          (product_id,location_id,quantity,unit,purchase_date,expiry_date,
           unit_price,store,lot_code,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (product_id,int(p.get("location_id") or 1),quantity,
           str(p.get("unit") or product["unit"]),
           iso_date(p.get("purchase_date")) or date.today().isoformat(),
           iso_date(p.get("expiry_date")),number(p.get("unit_price"),0) or None,
           str(p.get("store") or ""),code,actor(p))).lastrowid
        c.execute("""INSERT INTO stock_transactions
          (product_id,lot_id,profile_id,action,quantity,unit_price,store,note)
          VALUES(?,?,?,'purchase',?,?,?,'Partij toegevoegd')""",
          (product_id,lot_id,actor(p),quantity,number(p.get("unit_price"),0) or None,
           str(p.get("store") or "")))
    return jsonify(id=lot_id,lot_code=code),201


@app.post("/api/lots/<int:lot_id>/action")
def lot_action(lot_id):
    p=body(); action=str(p.get("action") or "consume")
    if action not in {"consume","waste","adjust","open","move"}:
        return jsonify(error="Onbekende actie"),400
    with db() as c:
        lot=c.execute("SELECT * FROM stock_lots WHERE id=?",(lot_id,)).fetchone()
        if not lot:return jsonify(error="Partij niet gevonden"),404
        qty=number(p.get("quantity"),1,0); delta=0
        if action in {"consume","waste"}:
            qty=min(qty,lot["quantity"]);delta=-qty
            c.execute("""UPDATE stock_lots SET quantity=quantity-?,
              updated_at=CURRENT_TIMESTAMP WHERE id=?""",(qty,lot_id))
        elif action=="adjust":
            new=number(p.get("quantity"),lot["quantity"],0)
            delta=new-lot["quantity"];qty=abs(delta)
            c.execute("""UPDATE stock_lots SET quantity=?,
              updated_at=CURRENT_TIMESTAMP WHERE id=?""",(new,lot_id))
        elif action=="open":
            c.execute("""UPDATE stock_lots SET opened_at=?,
              updated_at=CURRENT_TIMESTAMP WHERE id=?""",(date.today().isoformat(),lot_id))
            shelf=c.execute("SELECT opened_shelf_days FROM products WHERE id=?",
                            (lot["product_id"],)).fetchone()
            if shelf and shelf["opened_shelf_days"]:
                exp=(date.today()+timedelta(days=int(shelf["opened_shelf_days"]))).isoformat()
                c.execute("""UPDATE stock_lots SET expiry_date=
                  CASE WHEN expiry_date IS NULL OR expiry_date>? THEN ? ELSE expiry_date END
                  WHERE id=?""",(exp,exp,lot_id))
        else:
            c.execute("""UPDATE stock_lots SET location_id=?,
              updated_at=CURRENT_TIMESTAMP WHERE id=?""",(int(p["location_id"]),lot_id))
        c.execute("""INSERT INTO stock_transactions
          (product_id,lot_id,profile_id,action,quantity,unit_price,store,note)
          VALUES(?,?,?,?,?,?,?,?)""",
          (lot["product_id"],lot_id,actor(p),action,qty,lot["unit_price"],
           lot["store"],str(p.get("note") or "")))
    return jsonify(ok=True,delta=delta)


@app.get("/api/barcode/<barcode>")
def barcode_lookup(barcode):
    barcode=re.sub(r"\s+","",barcode)
    with db() as c:
        local=c.execute("""SELECT p.* FROM barcodes b JOIN products p
          ON p.id=b.product_id WHERE b.barcode=?""",(barcode,)).fetchone()
        if local:return jsonify(found=True,local=True,product=dict(local))
        lot=c.execute("""SELECT p.*,l.id lot_id,l.lot_code,l.quantity,l.expiry_date
          FROM stock_lots l JOIN products p ON p.id=l.product_id
          WHERE l.lot_code=?""",(barcode.upper(),)).fetchone()
        if lot:return jsonify(found=True,local=True,lot=dict(lot))
    try:result=open_food_facts(barcode)
    except RuntimeError as error:return jsonify(found=False,error=str(error)),502
    return jsonify(found=bool(result),local=False,product=result)


@app.post("/api/expiry-estimate")
def expiry_estimate():
    p=body()
    with db() as c:
        loc=c.execute("SELECT * FROM locations WHERE id=?",
                      (int(p.get("location_id") or 1),)).fetchone()
        if not loc:return jsonify(error="Locatie niet gevonden"),400
        local=estimate_local(c,str(p.get("name") or ""),str(p.get("category") or ""),
                             loc["kind"],bool(p.get("opened")))
        result=local
        if not result or p.get("force_ai"):
            try:
                result=estimate_gemini(c,str(p.get("name") or ""),
                                       str(p.get("category") or ""),loc["name"],
                                       bool(p.get("opened"))) or local
            except RuntimeError as error:
                if not local:return jsonify(error=str(error)),502
        if not result:
            result={"days":7 if loc["kind"]=="fridge" else
                    90 if loc["kind"]=="freezer" else 30,
                    "source":"fallback","confidence":"low"}
        result["expiry_date"]=(date.today()+timedelta(days=int(result["days"]))).isoformat()
        result["location"]=loc["name"]
    return jsonify(result)


@app.post("/api/shelf-rules")
def save_shelf_rule():
    p=body()
    with db() as c:
        loc=c.execute("SELECT kind FROM locations WHERE id=?",(int(p["location_id"]),)).fetchone()
        if not loc:return jsonify(error="Locatie niet gevonden"),400
        c.execute("""INSERT INTO shelf_life_rules
          (name_pattern,category,location_kind,unopened_days,opened_days,source)
          VALUES(?,?,?,?,?,'learned') ON CONFLICT(name_pattern,category,location_kind)
          DO UPDATE SET unopened_days=excluded.unopened_days,
          opened_days=excluded.opened_days,source='learned'""",
          (str(p.get("name_pattern") or "").lower().strip(),
           str(p.get("category") or "").lower().strip(),loc["kind"],
           int(p["unopened_days"]),p.get("opened_days") or None))
    return jsonify(ok=True)


@app.get("/api/locations")
def locations():
    with db() as c:return jsonify([dict(r) for r in c.execute(
        "SELECT * FROM locations ORDER BY is_fixed DESC,name")])


@app.post("/api/locations")
def create_location():
    p=body();name=str(p.get("name") or "").strip()
    if not name:return jsonify(error="Naam is verplicht"),400
    try:
        with db() as c:
            new_id=c.execute("INSERT INTO locations(name,kind,emoji) VALUES(?,?,?)",
                (name,str(p.get("kind") or "custom"),str(p.get("emoji") or "📦"))).lastrowid
        return jsonify(id=new_id),201
    except sqlite3.IntegrityError:return jsonify(error="Deze locatie bestaat al"),409


@app.delete("/api/locations/<int:location_id>")
def delete_location(location_id):
    with db() as c:
        loc=c.execute("SELECT * FROM locations WHERE id=?",(location_id,)).fetchone()
        if not loc or loc["is_fixed"]:
            return jsonify(error="Vaste locaties kunnen niet worden verwijderd"),400
        if c.execute("SELECT 1 FROM stock_lots WHERE location_id=? AND quantity>0",
                     (location_id,)).fetchone():
            return jsonify(error="Verplaats eerst de aanwezige voorraad"),409
        c.execute("DELETE FROM locations WHERE id=?",(location_id,))
    return "",204


@app.get("/api/dashboard")
def dashboard():
    with db() as c:
        refresh_notifications(c)
        products_count=c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        units=c.execute("SELECT COALESCE(SUM(quantity),0) FROM stock_lots").fetchone()[0]
        expiring=c.execute("""SELECT COUNT(*) FROM stock_lots WHERE quantity>0
          AND expiry_date IS NOT NULL AND expiry_date<=date('now','+7 day')""").fetchone()[0]
        low=c.execute("""SELECT COUNT(*) FROM ("""+product_query()+"""
          GROUP BY p.id HAVING stock<=p.minimum AND p.minimum>0)""").fetchone()[0]
        recent=[dict(r) for r in c.execute("""SELECT t.*,p.name,pr.name profile_name
          FROM stock_transactions t JOIN products p ON p.id=t.product_id
          LEFT JOIN profiles pr ON pr.id=t.profile_id
          ORDER BY t.created_at DESC LIMIT 8""")]
    return jsonify(products=products_count,units=units,expiring=expiring,low=low,recent=recent)


@app.get("/api/stats")
def stats():
    days=min(max(int(request.args.get("days",30)),7),3650)
    since=(date.today()-timedelta(days=days)).isoformat()
    with db() as c:
        totals=c.execute("""SELECT
          COALESCE(SUM(CASE WHEN action='purchase' THEN quantity*COALESCE(unit_price,0) ELSE 0 END),0) spent,
          COALESCE(SUM(CASE WHEN action='consume' THEN quantity ELSE 0 END),0) consumed,
          COALESCE(SUM(CASE WHEN action='waste' THEN quantity ELSE 0 END),0) wasted,
          COALESCE(SUM(CASE WHEN action='waste' THEN quantity*COALESCE(unit_price,0) ELSE 0 END),0) waste_value
          FROM stock_transactions WHERE date(created_at)>=?""",(since,)).fetchone()
        timeline=[dict(r) for r in c.execute("""SELECT date(created_at) day,
          SUM(CASE WHEN action='purchase' THEN quantity*COALESCE(unit_price,0) ELSE 0 END) spent,
          SUM(CASE WHEN action='consume' THEN quantity ELSE 0 END) consumed,
          SUM(CASE WHEN action='waste' THEN quantity ELSE 0 END) wasted
          FROM stock_transactions WHERE date(created_at)>=?
          GROUP BY date(created_at) ORDER BY day""",(since,))]
        waste=[dict(r) for r in c.execute("""SELECT p.name,SUM(t.quantity) quantity,
          SUM(t.quantity*COALESCE(t.unit_price,0)) value
          FROM stock_transactions t JOIN products p ON p.id=t.product_id
          WHERE t.action='waste' AND date(t.created_at)>=?
          GROUP BY p.id ORDER BY quantity DESC LIMIT 8""",(since,))]
        stores=[dict(r) for r in c.execute("""SELECT
          COALESCE(NULLIF(store,''),'Onbekend') store,
          SUM(quantity*COALESCE(unit_price,0)) spent
          FROM stock_transactions WHERE action='purchase' AND date(created_at)>=?
          GROUP BY store ORDER BY spent DESC""",(since,))]
    return jsonify(**dict(totals),timeline=timeline,waste_products=waste,
                   stores=stores,days=days)


@app.get("/api/history")
def history():
    with db() as c:
        rows=[dict(r) for r in c.execute("""SELECT t.*,p.name,pr.name profile_name,l.lot_code
          FROM stock_transactions t JOIN products p ON p.id=t.product_id
          LEFT JOIN profiles pr ON pr.id=t.profile_id
          LEFT JOIN stock_lots l ON l.id=t.lot_id
          ORDER BY t.created_at DESC LIMIT 300""")]
    return jsonify(rows)


@app.get("/api/notifications")
def notifications():
    with db() as c:
        refresh_notifications(c)
        rows=[dict(r) for r in c.execute("""SELECT * FROM notifications
          ORDER BY is_read,due_at,created_at DESC LIMIT 100""")]
    return jsonify(rows)


@app.post("/api/notifications/read")
def read_notifications():
    with db() as c:c.execute("UPDATE notifications SET is_read=1")
    return jsonify(ok=True)


@app.get("/api/shopping")
def shopping():
    with db() as c:
        manual=[dict(r) for r in c.execute(
          "SELECT *,0 automatic FROM shopping_items ORDER BY checked,name")]
        automatic=[dict(r) for r in c.execute(product_query()+
          " GROUP BY p.id HAVING stock<=p.minimum AND p.minimum>0 ORDER BY p.name")]
    auto=[{"product_id":r["id"],"name":r["name"],
           "quantity":max(r["minimum"]-r["stock"],1),"unit":r["unit"],
           "checked":0,"automatic":1} for r in automatic]
    return jsonify(auto+manual)


@app.post("/api/shopping")
def add_shopping():
    p=body();name=str(p.get("name") or "").strip()
    if not name:return jsonify(error="Naam is verplicht"),400
    with db() as c:
        new_id=c.execute("""INSERT INTO shopping_items(name,quantity,unit,product_id)
          VALUES(?,?,?,?)""",(name,number(p.get("quantity"),1,.01),
          str(p.get("unit") or "stuks"),p.get("product_id") or None)).lastrowid
    return jsonify(id=new_id),201


@app.patch("/api/shopping/<int:item_id>")
def update_shopping(item_id):
    with db() as c:c.execute("UPDATE shopping_items SET checked=? WHERE id=?",
                             (1 if body().get("checked") else 0,item_id))
    return "",204


@app.delete("/api/shopping/<int:item_id>")
def delete_shopping(item_id):
    with db() as c:c.execute("DELETE FROM shopping_items WHERE id=?",(item_id,))
    return "",204


@app.get("/api/labels")
def labels():
    with db() as c:
        rows=[dict(r) for r in c.execute("""SELECT j.*,p.name,p.brand,p.unit,
          l.quantity,l.expiry_date,l.lot_code,loc.name location
          FROM label_jobs j JOIN products p ON p.id=j.product_id
          LEFT JOIN stock_lots l ON l.id=j.lot_id
          LEFT JOIN locations loc ON loc.id=l.location_id
          ORDER BY CASE j.status WHEN 'preview' THEN 0 WHEN 'queued' THEN 1 ELSE 2 END,
          j.created_at DESC""")]
    return jsonify(rows)


@app.post("/api/labels")
def create_label():
    p=body()
    with db() as c:
        if not c.execute("SELECT 1 FROM products WHERE id=?",(int(p["product_id"]),)).fetchone():
            return jsonify(error="Product niet gevonden"),404
        new_id=c.execute("""INSERT INTO label_jobs
          (product_id,lot_id,status,copies,template,label_size) VALUES(?,?,?,?,?,?)""",
          (int(p["product_id"]),p.get("lot_id") or None,str(p.get("status") or "preview"),
           int(p.get("copies") or 1),str(p.get("template") or setting(c,"label_template","compact")),
           str(p.get("label_size") or setting(c,"label_size","57x32")))).lastrowid
    return jsonify(id=new_id),201


@app.patch("/api/labels/<int:job_id>")
def update_label(job_id):
    status=str(body().get("status") or "queued")
    with db() as c:
        c.execute("""UPDATE label_jobs SET status=?,
          printed_at=CASE WHEN ?='printed' THEN CURRENT_TIMESTAMP ELSE printed_at END
          WHERE id=?""",(status,status,job_id))
    return jsonify(ok=True)


@app.get("/api/barcode.svg")
def barcode_svg():
    value=request.args.get("value","HOME-STOCK")[:80]
    output=io.BytesIO()
    Code128(value,writer=SVGWriter()).write(output,
      {"module_height":8,"font_size":6,"text_distance":2,"quiet_zone":1})
    return Response(output.getvalue(),mimetype="image/svg+xml",
                    headers={"Cache-Control":"public,max-age=86400"})


@app.get("/api/recipes")
def recipes():
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT * FROM recipes ORDER BY name")]
        for recipe in rows:
            recipe["items"]=[dict(r) for r in c.execute("""SELECT ri.*,p.name product_name
              FROM recipe_items ri LEFT JOIN products p ON p.id=ri.product_id
              WHERE recipe_id=?""",(recipe["id"],))]
    return jsonify(rows)


@app.post("/api/recipes")
def create_recipe():
    p=body();name=str(p.get("name") or "").strip()
    if not name:return jsonify(error="Naam is verplicht"),400
    with db() as c:
        rid=c.execute("""INSERT INTO recipes
          (name,servings,instructions,prep_minutes,emoji) VALUES(?,?,?,?,?)""",
          (name,int(p.get("servings") or 2),str(p.get("instructions") or ""),
           int(p.get("prep_minutes") or 0),str(p.get("emoji") or "🍽️"))).lastrowid
        for item in p.get("items",[]):
            c.execute("""INSERT INTO recipe_items
              (recipe_id,product_id,ingredient,amount,unit) VALUES(?,?,?,?,?)""",
              (rid,item.get("product_id") or None,str(item.get("ingredient") or ""),
               number(item.get("amount"),1,.01),str(item.get("unit") or "stuks")))
    return jsonify(id=rid),201


@app.delete("/api/recipes/<int:recipe_id>")
def delete_recipe(recipe_id):
    with db() as c:c.execute("DELETE FROM recipes WHERE id=?",(recipe_id,))
    return "",204


@app.post("/api/recipes/<int:recipe_id>/shopping")
def recipe_shopping(recipe_id):
    servings=number(body().get("servings"),2,.1)
    with db() as c:
        recipe=c.execute("SELECT * FROM recipes WHERE id=?",(recipe_id,)).fetchone()
        if not recipe:return jsonify(error="Recept niet gevonden"),404
        factor=servings/recipe["servings"]
        for item in c.execute("SELECT * FROM recipe_items WHERE recipe_id=?",
                              (recipe_id,)).fetchall():
            stock=0
            if item["product_id"]:
                stock=c.execute("""SELECT COALESCE(SUM(quantity),0) FROM stock_lots
                  WHERE product_id=?""",(item["product_id"],)).fetchone()[0]
            needed=item["amount"]*factor
            if stock<needed:
                c.execute("""INSERT INTO shopping_items(name,quantity,unit,product_id)
                  VALUES(?,?,?,?)""",(item["ingredient"],needed-stock,item["unit"],
                                      item["product_id"]))
    return jsonify(ok=True)


@app.get("/api/meal-plan")
def meal_plan():
    start=request.args.get("start",date.today().isoformat())
    end=request.args.get("end",(date.today()+timedelta(days=30)).isoformat())
    with db() as c:
        rows=[dict(r) for r in c.execute("""SELECT m.*,r.name recipe_name,r.emoji
          FROM meal_plan m JOIN recipes r ON r.id=m.recipe_id
          WHERE plan_date BETWEEN ? AND ? ORDER BY plan_date,meal""",(start,end))]
    return jsonify(rows)


@app.post("/api/meal-plan")
def create_meal_plan():
    p=body()
    with db() as c:
        new_id=c.execute("""INSERT INTO meal_plan
          (plan_date,meal,recipe_id,servings,note) VALUES(?,?,?,?,?)""",
          (iso_date(p["plan_date"]),str(p.get("meal") or "avondeten"),
           int(p["recipe_id"]),int(p.get("servings") or 2),
           str(p.get("note") or ""))).lastrowid
    return jsonify(id=new_id),201


@app.delete("/api/meal-plan/<int:plan_id>")
def delete_meal_plan(plan_id):
    with db() as c:c.execute("DELETE FROM meal_plan WHERE id=?",(plan_id,))
    return "",204


@app.get("/api/profiles")
def profiles():
    with db() as c:return jsonify([dict(r) for r in c.execute(
      "SELECT id,name,color,avatar,is_admin,created_at FROM profiles ORDER BY id")])


@app.post("/api/profiles")
def create_profile():
    p=body();name=str(p.get("name") or "").strip()
    if not name:return jsonify(error="Naam is verplicht"),400
    pin=str(p.get("pin") or "")
    pin_hash=hashlib.sha256(pin.encode()).hexdigest() if pin else None
    try:
        with db() as c:
            new_id=c.execute("""INSERT INTO profiles(name,color,avatar,pin_hash)
              VALUES(?,?,?,?)""",(name,str(p.get("color") or "#14956f"),
              str(p.get("avatar") or "👤"),pin_hash)).lastrowid
        return jsonify(id=new_id),201
    except sqlite3.IntegrityError:return jsonify(error="Deze naam bestaat al"),409


@app.get("/api/settings")
def get_settings():
    with db() as c:
        values={r["key"]:r["value"] for r in c.execute("SELECT key,value FROM settings")
                if r["key"]!="gemini_api_key"}
        values["gemini_configured"]=bool(setting(c,"gemini_api_key"))
    return jsonify(values)


@app.put("/api/settings")
def save_settings():
    p=body();allowed={"gemini_api_key","gemini_model","expiry_warning_days",
                      "label_size","label_template","currency"}
    with db() as c:
        for key,value in p.items():
            if key in allowed and value not in (None,""):
                c.execute("""INSERT INTO settings(key,value) VALUES(?,?)
                  ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                  updated_at=CURRENT_TIMESTAMP""",(key,str(value)))
    return jsonify(ok=True)


@app.get("/api/export.csv")
def export_csv():
    output=io.StringIO()
    fields=["name","brand","stock","unit","minimum","category",
            "locations","barcodes","next_expiry"]
    writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader()
    with db() as c:
        for row in c.execute(product_query()+" GROUP BY p.id ORDER BY p.name"):
            writer.writerow({field:row[field] for field in fields})
    return Response(output.getvalue(),mimetype="text/csv",
      headers={"Content-Disposition":"attachment; filename=home-stock-v0.2.csv"})


@app.get("/api/backup.json")
def backup():
    names=["products","locations","profiles","stock_lots","barcodes",
           "stock_transactions","shelf_life_rules","shopping_items","label_jobs",
           "notifications","recipes","recipe_items","meal_plan"]
    with db() as c:
        payload={"version":APP_VERSION,"created":datetime.now().isoformat(),
                 **{name:[dict(r) for r in c.execute(f"SELECT * FROM {name}")]
                    for name in names}}
    return Response(json.dumps(payload,ensure_ascii=False,indent=2),
      mimetype="application/json",
      headers={"Content-Disposition":"attachment; filename=home-stock-backup.json"})


init_db()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)
