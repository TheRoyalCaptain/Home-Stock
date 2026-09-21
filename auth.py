"""Database-backed authentication; household profiles are not login accounts."""
import hashlib
import os
import secrets
import time

from flask import g, jsonify, redirect, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash


def install_auth(app, db):
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
    cookie = "home_stock_session"
    secure = os.environ.get("HOME_STOCK_SECURE_COOKIE") == "1"
    default_hash = generate_password_hash("admin", method="scrypt")
    with db() as c:
        c.executescript("""
          CREATE TABLE IF NOT EXISTS auth_users (
            id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, must_change INTEGER NOT NULL DEFAULT 1,
            role TEXT NOT NULL DEFAULT 'member', profile_id INTEGER);
          CREATE TABLE IF NOT EXISTS auth_sessions (
            token_hash TEXT PRIMARY KEY, user_id INTEGER, csrf TEXT NOT NULL,
            expires REAL NOT NULL, FOREIGN KEY(user_id) REFERENCES auth_users(id));
          CREATE TABLE IF NOT EXISTS auth_attempts (
            bucket TEXT PRIMARY KEY, attempts INTEGER NOT NULL, reset_at REAL NOT NULL);
        """)
        c.execute("""INSERT OR IGNORE INTO auth_users
            (id,username,password_hash,must_change,role,profile_id)
            VALUES (1,'admin',?,1,'admin',1)""", (default_hash,))

    def digest(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def new_session(user_id=None, connection=None):
        token = secrets.token_urlsafe(32)
        row = dict(token_hash=digest(token), user_id=user_id,
                   csrf=secrets.token_urlsafe(32), expires=time.time() + (43200 if user_id else 1800))
        def write(c):
            if getattr(g, "auth_session", None):
                c.execute("DELETE FROM auth_sessions WHERE token_hash=?", (g.auth_session["token_hash"],))
            c.execute("DELETE FROM auth_sessions WHERE expires < ?", (time.time(),))
            c.execute("INSERT INTO auth_sessions VALUES (:token_hash,:user_id,:csrf,:expires)", row)
        if connection is not None:
            write(connection)
        else:
            with db() as c:
                write(c)
        g.auth_session = row
        g.new_auth_token = token

    def failure(message, status=403):
        if request.path.startswith("/api/"):
            return jsonify(error=message), status
        return render_template("auth.html", mode="error", error=message), status

    @app.before_request
    def require_auth():
        g.auth_session = None
        g.auth_user = None
        token = request.cookies.get(cookie, "")
        if token:
            with db() as c:
                row = c.execute("SELECT * FROM auth_sessions WHERE token_hash=? AND expires>?",
                                (digest(token), time.time())).fetchone()
                if row:
                    g.auth_session = dict(row)
                    if row["user_id"]:
                        user = c.execute("SELECT * FROM auth_users WHERE id=?", (row["user_id"],)).fetchone()
                        g.auth_user = dict(user) if user else None
        public = request.endpoint in {"login", "static", "health", "service_worker"}
        if not public and not g.auth_user:
            return failure("Log opnieuw in om verder te gaan.", 401) if request.path.startswith("/api/") else redirect("/login")
        if g.auth_user and g.auth_user["must_change"] and request.endpoint not in {
                "login", "change_password", "logout", "static", "health", "service_worker"}:
            return (jsonify(error="Wijzig eerst je standaardwachtwoord.", password_change_required=True), 403) if request.path.startswith("/api/") else redirect("/account/password")
        if g.auth_user and g.auth_user["role"] != "admin" and (
                request.path.startswith("/account/users") or
                (request.path in {"/api/settings", "/api/profiles", "/api/printers/test"} and request.method not in {"GET", "HEAD"})):
            return failure("Alleen beheerders mogen dit aanpassen.")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            csrf = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            if not g.auth_session or not secrets.compare_digest(csrf, g.auth_session["csrf"]):
                return failure("Sessie verlopen of ongeldig. Vernieuw de pagina en probeer opnieuw.")

    @app.context_processor
    def auth_context():
        return dict(csrf_token=g.auth_session["csrf"] if g.auth_session else "",
                    auth_username=g.auth_user["username"] if g.auth_user else "",
                    auth_role=g.auth_user["role"] if g.auth_user else "",
                    auth_profile_id=g.auth_user["profile_id"] if g.auth_user else "")

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = ("public,max-age=86400" if request.endpoint == "static"
                                              else "no-cache" if request.endpoint == "service_worker"
                                              else "no-store")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' https: data:; media-src 'self' blob:; "
            "connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'self'; form-action 'self'")
        if getattr(g, "new_auth_token", None):
            response.set_cookie(cookie, g.new_auth_token, httponly=True,
                                secure=secure or request.is_secure, samesite="Lax", path="/")
        if getattr(g, "delete_auth_cookie", False):
            response.delete_cookie(cookie, path="/")
        return response

    def rate_limited(keys):
        now = time.time()
        with db() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute("DELETE FROM auth_attempts WHERE reset_at<=?", (now,))
            for key in keys:
                row = c.execute("SELECT attempts FROM auth_attempts WHERE bucket=?", (key,)).fetchone()
                if row and row["attempts"] >= 5:
                    return True
            for key in keys:
                c.execute("""INSERT INTO auth_attempts VALUES (?,1,?)
                    ON CONFLICT(bucket) DO UPDATE SET attempts=attempts+1""", (key, now+900))
        return False

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.auth_user:
            return redirect("/account/password" if g.auth_user["must_change"] else "/")
        if not g.auth_session:
            new_session()
        error = None
        status = 200
        if request.method == "POST":
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")
            keys = ["ip:"+str(request.remote_addr), "user:"+digest(username.lower())]
            if rate_limited(keys):
                error, status = "Te veel pogingen. Probeer het over 15 minuten opnieuw.", 429
            else:
                with db() as c:
                    user = c.execute("SELECT * FROM auth_users WHERE username=?", (username,)).fetchone()
                valid = len(password) <= 256 and check_password_hash(user["password_hash"] if user else default_hash, password)
                if user and valid:
                    with db() as c:
                        # Also enforce the change if a legacy record still uses admin.
                        if check_password_hash(user["password_hash"], "admin"):
                            c.execute("UPDATE auth_users SET must_change=1 WHERE id=?", (user["id"],))
                        for key in keys:
                            c.execute("DELETE FROM auth_attempts WHERE bucket=?", (key,))
                    new_session(user["id"])
                    return redirect("/")
                error, status = "Gebruikersnaam of wachtwoord klopt niet.", 401
        return render_template("auth.html", mode="login", error=error), status

    @app.route("/account/password", methods=["GET", "POST"])
    def change_password():
        error = None
        status = 200
        if request.method == "POST":
            current = request.form.get("current_password", "")
            password = request.form.get("password", "")
            if rate_limited(["password:"+str(g.auth_user["id"])]):
                error, status = "Te veel pogingen. Probeer het over 15 minuten opnieuw.", 429
            elif len(current)>256 or not check_password_hash(g.auth_user["password_hash"], current):
                error, status = "Je huidige wachtwoord klopt niet.", 400
            elif len(password)<12 or len(password)>256 or password.strip().lower()=="admin":
                error, status = "Kies een nieuw wachtwoord van 12 tot 256 tekens.", 400
            elif password != request.form.get("password_confirm"):
                error, status = "De nieuwe wachtwoorden komen niet overeen.", 400
            elif check_password_hash(g.auth_user["password_hash"], password):
                error, status = "Kies een ander wachtwoord dan je huidige.", 400
            else:
                hashed = generate_password_hash(password, method="scrypt")
                with db() as c:
                    c.execute("UPDATE auth_users SET password_hash=?,must_change=0 WHERE id=?",
                              (hashed, g.auth_user["id"]))
                    c.execute("DELETE FROM auth_sessions WHERE user_id=?", (g.auth_user["id"],))
                    c.execute("DELETE FROM auth_attempts WHERE bucket=?", ("password:"+str(g.auth_user["id"]),))
                    new_session(g.auth_user["id"], c)
                return redirect("/")
        return render_template("auth.html", mode="password", error=error,
                               forced=bool(g.auth_user["must_change"])), status

    @app.post("/logout")
    def logout():
        with db() as c:
            c.execute("DELETE FROM auth_sessions WHERE token_hash=?", (g.auth_session["token_hash"],))
        g.delete_auth_cookie = True
        return redirect("/login")

    @app.route("/account/users", methods=["GET", "POST"])
    def manage_users():
        error = None
        status = 200
        if request.method == "POST":
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")
            role = request.form.get("role", "member")
            if not username or len(username)>80 or not all(ch.isascii() and (ch.isalnum() or ch in "._-") for ch in username):
                error, status = "Gebruik 1 tot 80 letters, cijfers, punten, streepjes of underscores.", 400
            elif not 12<=len(password)<=256 or password.strip().lower()=="admin":
                error, status = "Gebruik een tijdelijk wachtwoord van 12 tot 256 tekens.", 400
            elif role not in {"admin", "member"}:
                error, status = "Kies een geldige rol.", 400
            else:
                hashed = generate_password_hash(password, method="scrypt")
                with db() as c:
                    c.execute("BEGIN IMMEDIATE")
                    if c.execute("SELECT id FROM auth_users WHERE username=?", (username,)).fetchone():
                        error, status = "Deze gebruikersnaam bestaat al.", 400
                    else:
                        profile_name = username
                        while c.execute("SELECT id FROM profiles WHERE name=?", (profile_name,)).fetchone():
                            profile_name = username + " " + secrets.token_hex(3)
                        profile = c.execute("INSERT INTO profiles (name,avatar,is_admin) VALUES (?,'👤',?)",
                                            (profile_name, int(role=="admin"))).lastrowid
                        c.execute("""INSERT INTO auth_users
                            (username,password_hash,must_change,role,profile_id)
                            VALUES (?,?,1,?,?)""", (username, hashed, role, profile))
                        return redirect("/account/users?created=1")
        with db() as c:
            users = c.execute("SELECT username,role,must_change FROM auth_users ORDER BY username").fetchall()
        return render_template("users.html", users=users, error=error), status
