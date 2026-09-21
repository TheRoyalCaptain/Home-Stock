"""Run with python -m unittest discover -s tests."""
import os
import re
import tempfile
import unittest

test_data = tempfile.TemporaryDirectory()
os.environ["HOME_STOCK_DATA_DIR"] = test_data.name
from app import app, db


class AuthenticationTest(unittest.TestCase):
    def token(self, client, path):
        response = client.get(path)
        return re.search(r'name="csrf_token" value="([^"]+)"', response.text)[1]

    def login(self, client, username, password):
        return client.post("/login", data=dict(
            csrf_token=self.token(client, "/login"), username=username, password=password))

    def change(self, client, current, password):
        return client.post("/account/password", data=dict(
            csrf_token=self.token(client, "/account/password"),
            current_password=current, password=password, password_confirm=password))

    def test_complete_security_flow(self):
        anon = app.test_client()
        # Every API rule is denied before its handler, including exports/images.
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith("/api/"):
                path = re.sub(r"<(?:[^:>]+:)?[^>]+>", "1", rule.rule)
                for method in rule.methods - {"OPTIONS", "HEAD"}:
                    self.assertEqual(anon.open(path, method=method).status_code, 401, (path, method))
        self.assertEqual(anon.get("/").location, "/login")
        self.assertEqual(anon.get("/health").status_code, 200)
        self.assertEqual(anon.post("/login", data=dict(username="admin", password="admin")).status_code, 403)
        admin = app.test_client()
        self.assertEqual(self.login(admin, "admin", "admin").status_code, 302)
        old_cookie = admin.get_cookie("home_stock_session").value
        self.assertEqual(admin.get("/").location, "/account/password")
        self.assertEqual(admin.get("/api/backup.json").status_code, 403)
        self.assertEqual(admin.get("/account/users").location, "/account/password")
        self.assertEqual(self.change(admin, "admin", "admin").status_code, 400)
        self.assertEqual(self.change(admin, "admin", "A long unique passphrase!").status_code, 302)
        self.assertNotEqual(admin.get_cookie("home_stock_session").value, old_cookie)
        replay = app.test_client()
        replay.set_cookie("home_stock_session", old_cookie)
        self.assertEqual(replay.get("/api/products").status_code, 401)
        response = admin.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response.headers["Cache-Control"])
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', response.text)[1]
        self.assertEqual(admin.post("/api/products", json={"name":"Test"}).status_code, 403)
        self.assertEqual(admin.post("/api/products", headers={"X-CSRF-Token":csrf},
                                    json={"name":"Test","quantity":1,"location_id":1}).status_code, 201)
        token = self.token(admin, "/account/users")
        self.assertEqual(admin.post("/account/users", data=dict(csrf_token=token,
            username="simon", password="Temporary passphrase!", role="member")).status_code, 302)
        self.assertEqual(admin.post("/account/users", data=dict(csrf_token=token,
            username="simon", password="Temporary passphrase!", role="member")).status_code, 400)
        member = app.test_client()
        self.assertEqual(self.login(member, "simon", "Temporary passphrase!").status_code, 302)
        self.assertEqual(member.get("/api/products").status_code, 403)
        self.assertEqual(self.change(member, "Temporary passphrase!", "Another unique passphrase!").status_code, 302)
        self.assertEqual(member.get("/api/products").status_code, 200)
        self.assertEqual(member.get("/account/users").status_code, 403)
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', member.get("/").text)[1]
        self.assertEqual(member.put("/api/settings", headers={"X-CSRF-Token":csrf}, json={}).status_code, 403)
        created = member.post("/api/products", headers={"X-CSRF-Token":csrf},
            json={"name":"Owned by Simon","quantity":1,"location_id":1,"profile_id":1})
        self.assertEqual(created.status_code, 201)
        with db() as c:
            profile = c.execute("SELECT profile_id FROM auth_users WHERE username='simon'").fetchone()[0]
            self.assertEqual(c.execute("SELECT profile_id FROM stock_transactions ORDER BY id DESC").fetchone()[0], profile)
            self.assertTrue(c.execute("SELECT password_hash FROM auth_users LIMIT 1").fetchone()[0].startswith("scrypt:"))
        self.assertEqual(member.post("/logout", data={"csrf_token":csrf}).status_code, 302)
        self.assertEqual(member.get("/api/products").status_code, 401)
        blocked = app.test_client()
        for _ in range(5):
            self.assertEqual(self.login(blocked, "admin", "wrong").status_code, 401)
        self.assertEqual(self.login(blocked, "admin", "wrong").status_code, 429)
        with db() as c:
            c.execute("UPDATE auth_sessions SET expires=0")
        self.assertEqual(admin.get("/api/products").status_code, 401)


if __name__ == "__main__":
    unittest.main()
