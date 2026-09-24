"""Run with python -m unittest discover -s tests."""
import io
import json
import os
import re
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from barcode import Code128
from barcode.writer import ImageWriter

test_data = tempfile.TemporaryDirectory()
os.environ["HOME_STOCK_DATA_DIR"] = test_data.name
from app import app, db
import app as app_module


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

    def test_server_barcode_decoder(self):
        image = io.BytesIO()
        Code128("VP001-A", writer=ImageWriter()).write(image)
        decoded = app_module.decode_barcode_image(image.getvalue())
        self.assertEqual(decoded[0]["text"], "VP001-A")

    def test_gemini_preparation_uses_name_and_ingredients(self):
        raw = {"candidates":[{"content":{"parts":[{"text":json.dumps({
            "instructions":"Magnetron: 4-5 min op 700 W, halverwege omscheppen."})}]}}]}
        response = MagicMock()
        response.__enter__.return_value = io.BytesIO(json.dumps(raw).encode())
        with db() as c:
            c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('gemini_api_key','test-key')")
            with patch.object(app_module.urllib.request, "urlopen", return_value=response) as opened:
                result = app_module.generate_preparation_gemini(
                    c, "Vegetarische pasta", "pasta, tomaat en kaas", 500)
            c.execute("DELETE FROM settings WHERE key='gemini_api_key'")
        self.assertEqual(result, "Magnetron: 4-5 min op 700 W, halverwege omscheppen.")
        prompt = json.loads(opened.call_args.args[0].data)["contents"][0]["parts"][0]["text"]
        self.assertIn("Vegetarische pasta", prompt)
        self.assertIn("pasta, tomaat en kaas", prompt)
        self.assertIn("tijdsduur", prompt)
        self.assertIn("watt", prompt)
        self.assertIn("°C", prompt)
        self.assertIn("500 gram", prompt)

    def test_complete_security_flow(self):
        anon = app.test_client()
        manifest = anon.get("/static/manifest.webmanifest")
        self.assertEqual(manifest.status_code, 200)
        manifest.close()
        service_worker = anon.get("/service-worker.js")
        self.assertEqual(service_worker.status_code, 200)
        self.assertEqual(service_worker.headers["Service-Worker-Allowed"], "/")
        service_worker.close()
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
            member_id = c.execute("SELECT id FROM auth_users WHERE username='simon'").fetchone()[0]
            self.assertEqual(c.execute("SELECT profile_id FROM stock_transactions ORDER BY id DESC").fetchone()[0], profile)
            self.assertTrue(c.execute("SELECT password_hash FROM auth_users LIMIT 1").fetchone()[0].startswith("scrypt:"))
        admin_csrf = re.search(r'name="csrf-token" content="([^"]+)"', admin.get("/").text)[1]
        self.assertEqual(admin.post(f"/account/users/{member_id}/toggle",
            data={"csrf_token":admin_csrf}).status_code, 302)
        self.assertEqual(member.get("/api/products").status_code, 401)
        self.assertEqual(admin.post(f"/account/users/{member_id}/toggle",
            data={"csrf_token":admin_csrf}).status_code, 302)
        self.assertEqual(admin.post(f"/account/users/{member_id}/reset", data={
            "csrf_token":admin_csrf,"password":"Fresh temporary password!"}).status_code, 302)
        renewed = app.test_client()
        self.assertEqual(self.login(renewed, "simon", "Fresh temporary password!").status_code, 302)
        self.assertEqual(renewed.get("/").location, "/account/password")
        renewed_csrf = self.token(renewed, "/account/password")
        self.assertEqual(self.change(renewed, "Fresh temporary password!",
                                     "Final unique passphrase!").status_code, 302)
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', renewed.get("/").text)[1]
        self.assertEqual(renewed.post("/logout", data={"csrf_token":csrf}).status_code, 302)
        self.assertEqual(member.get("/api/products").status_code, 401)
        blocked = app.test_client()
        for _ in range(5):
            self.assertEqual(self.login(blocked, "admin", "wrong").status_code, 401)
        self.assertEqual(self.login(blocked, "admin", "wrong").status_code, 429)
        with db() as c:
            c.execute("UPDATE auth_sessions SET expires=0")
        self.assertEqual(admin.get("/api/products").status_code, 401)

    def test_direct_printer_api(self):
        with db() as c:
            c.execute("DELETE FROM auth_attempts")
        client = app.test_client()
        self.assertEqual(self.login(client, "admin", "A long unique passphrase!").status_code, 302)
        page = client.get("/")
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', page.text)[1]
        discovered = {"printers":[{"id":"Home_Stock_DYMO_450","name":"DYMO 450"}]}
        printed = {"ok":True,"printer":{"id":"Home_Stock_DYMO_450","name":"DYMO 450"}}
        with patch.object(app_module, "print_service", side_effect=[discovered, printed, printed]) as service:
            self.assertEqual(client.get("/api/printers").json, discovered)
            self.assertEqual(client.post("/api/printers/test", headers={"X-CSRF-Token":csrf}, json={}).status_code, 200)
            created = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Printproduct","quantity":1,"location_id":1,"create_label":True,
                "product_type":"homemade","contents":"Pasta en groente",
                "portion_grams":500,
                "preparation_instructions":"Verwarm 4 minuten en roer halverwege door.",
                "production_date":"2026-09-21","expiry_date":"2026-09-28"}).json
            self.assertRegex(created["short_code"], r"^PR\d{3}$")
            self.assertEqual(client.get("/api/barcode/"+created["short_code"]).json["product"]["id"], created["id"])
            response = client.post(f"/api/labels/{created['label_job_id']}/print",
                                   headers={"X-CSRF-Token":csrf}, json={})
            self.assertEqual(response.status_code, 200)
            payload = service.call_args_list[-1].args[1]
            self.assertEqual(payload["name"], "Printproduct")
            self.assertEqual(payload["short_code"], created["short_code"])
            self.assertEqual(payload["lot_code"], created["lot_code"])
            self.assertEqual(payload["contents"], "Pasta en groente")
            self.assertEqual(payload["preparation_instructions"], "Verwarm 4 minuten en roer halverwege door.")
            self.assertEqual(payload["portion_grams"], 500)
            self.assertIn("500 g", payload["detail"])
            self.assertEqual(payload["production_date"], "2026-09-21")
            self.assertEqual(payload["placed_by"], "Kevin")
            self.assertEqual(payload["copies"], 1)
            with db() as c:
                self.assertEqual(c.execute("SELECT status FROM label_jobs WHERE id=?",
                    (created["label_job_id"],)).fetchone()[0], "printed")

            batch = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Vegetarische pasta","quantity":1,"container_count":3,
                "unit":"bak","location_id":2,"create_label":True,
                "portion_grams":450,
                "product_type":"homemade","contents":"Pasta, tomaat en kaas",
                "production_date":"2026-09-21","expiry_date":"2026-12-21"})
            self.assertEqual(batch.status_code, 201)
            batch = batch.json
            self.assertEqual(batch["container_count"], 3)
            self.assertEqual(batch["lot_codes"], [f"{batch['short_code']}-{letter}" for letter in "ABC"])
            self.assertEqual(len(batch["lot_ids"]), 3)
            self.assertEqual(len(batch["label_job_ids"]), 3)
            detail = client.get(f"/api/products/{batch['id']}").json
            self.assertEqual(detail["product"]["stock"], 3)
            self.assertEqual([lot["quantity"] for lot in detail["lots"]], [1, 1, 1])
            self.assertEqual([lot["portion_grams"] for lot in detail["lots"]], [450, 450, 450])
            self.assertEqual(client.get("/api/barcode/"+batch["lot_codes"][1]).json["lot"]["lot_id"], batch["lot_ids"][1])

            consumed = client.post(f"/api/lots/{batch['lot_ids'][0]}/action",
                headers={"X-CSRF-Token":csrf}, json={"action":"consume","quantity":1})
            self.assertEqual(consumed.status_code, 200)
            detail = client.get(f"/api/products/{batch['id']}").json
            self.assertEqual(detail["product"]["stock"], 2)
            self.assertEqual([lot["quantity"] for lot in detail["lots"]], [0, 1, 1])

            extra = client.post(f"/api/products/{batch['id']}/lots",
                headers={"X-CSRF-Token":csrf}, json={"quantity":1,"container_count":2,
                    "unit":"bak","portion_grams":600,"location_id":2,"create_labels":True}).json
            self.assertEqual(extra["lot_codes"], [f"{batch['short_code']}-D", f"{batch['short_code']}-E"])
            self.assertEqual(len(extra["label_job_ids"]), 2)
            detail = client.get(f"/api/products/{batch['id']}").json
            self.assertEqual([lot["portion_grams"] for lot in detail["lots"][-2:]], [600, 600])

            with patch.object(app_module, "generate_preparation_gemini",
                              return_value="Verwarm goed en schep halverwege om."):
                prepared = client.post("/api/preparation-instructions", headers={
                    "X-CSRF-Token":csrf}, json={"name":"Pasta","contents":"tomaat en kaas"})
            self.assertEqual(prepared.status_code, 200)
            self.assertEqual(prepared.json["instructions"], "Verwarm goed en schep halverwege om.")

            with patch.object(app_module, "decode_barcode_image",
                              return_value=[{"text":batch["lot_codes"][1],"format":"Code128"}]):
                decoded = client.post("/api/barcode/decode", headers={
                    "X-CSRF-Token":csrf,"Content-Type":"image/jpeg"}, data=b"camera frame")
            self.assertEqual(decoded.status_code, 200)
            self.assertEqual(decoded.json["codes"][0]["text"], batch["lot_codes"][1])
            self.assertEqual(client.post("/api/barcode/decode", headers={
                "X-CSRF-Token":csrf,"Content-Type":"text/plain"}, data=b"x").status_code, 415)

            last = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Laatste portie","quantity":1,"unit":"bak","location_id":1}).json
            archived = client.post(f"/api/lots/{last['lot_id']}/action",
                headers={"X-CSRF-Token":csrf}, json={"action":"consume","quantity":1,
                    "archive_when_empty":True})
            self.assertEqual(archived.status_code, 200)
            self.assertTrue(archived.json["archived"])
            self.assertNotIn(last["id"], [p["id"] for p in client.get("/api/products").json])
            self.assertEqual(client.get(f"/api/products/{last['id']}").status_code, 200)
            self.assertTrue(any(row["product_id"]==last["id"] and row["action"]=="consume"
                                for row in client.get("/api/history").json))

            restored = client.post(f"/api/products/{last['id']}/lots",
                headers={"X-CSRF-Token":csrf}, json={"quantity":1,"location_id":1})
            self.assertEqual(restored.status_code, 201)
            self.assertIn(last["id"], [p["id"] for p in client.get("/api/products").json])

            keep = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Op nul bewaren","quantity":1,"location_id":1}).json
            kept = client.post(f"/api/lots/{keep['lot_id']}/action",
                headers={"X-CSRF-Token":csrf}, json={"action":"waste","quantity":1,
                    "archive_when_empty":False})
            self.assertFalse(kept.json["archived"])
            self.assertIn(keep["id"], [p["id"] for p in client.get("/api/products").json])

            # A scanned individual lot can be consumed and safely restored.
            scan = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Scanportie","quantity":1,"location_id":1}).json
            consumed = client.post(f"/api/barcode/{scan['lot_code']}/consume",
                headers={"X-CSRF-Token":csrf}, json={})
            self.assertEqual(consumed.status_code, 200)
            self.assertTrue(consumed.json["archived"])
            transaction_id = consumed.json["transaction_id"]
            undone = client.post(f"/api/history/{transaction_id}/undo",
                headers={"X-CSRF-Token":csrf}, json={})
            self.assertEqual(undone.status_code, 200)
            scan_detail = client.get(f"/api/products/{scan['id']}").json
            self.assertEqual(scan_detail["product"]["stock"], 1)
            self.assertEqual(scan_detail["lots"][0]["quantity"], 1)

            # Expired cleanup is logged as waste and can also be undone.
            expired = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Verlopen test","quantity":2,"location_id":1,
                "expiry_date":"2020-01-01"}).json
            cleaned = client.post("/api/expired/cleanup", headers={"X-CSRF-Token":csrf},
                json={})
            self.assertEqual(cleaned.status_code, 200)
            self.assertGreaterEqual(cleaned.json["lots"], 1)
            cleanup_tx = next(row for row in client.get("/api/history").json
                              if row["product_id"] == expired["id"] and row["action"] == "waste")
            self.assertEqual(client.post(f"/api/history/{cleanup_tx['id']}/undo",
                headers={"X-CSRF-Token":csrf}, json={}).status_code, 200)
            self.assertEqual(client.get(f"/api/products/{expired['id']}").json["product"]["stock"], 2)

            # Shelf-life templates and configurable notification schedule persist.
            rules = client.get("/api/shelf-rules").json
            self.assertTrue(rules)
            custom = client.post("/api/shelf-rules", headers={"X-CSRF-Token":csrf}, json={
                "name_pattern":"testmaaltijd","category":"test","location_id":1,
                "unopened_days":4,"opened_days":2})
            self.assertEqual(custom.status_code, 200)
            custom_rule = next(row for row in client.get("/api/shelf-rules").json
                               if row["name_pattern"] == "testmaaltijd")
            self.assertEqual(client.put(f"/api/shelf-rules/{custom_rule['id']}",
                headers={"X-CSRF-Token":csrf}, json={"name_pattern":"testmaaltijd",
                    "category":"test","location_kind":"fridge","unopened_days":5,
                    "opened_days":2}).status_code, 200)
            self.assertEqual(client.delete(f"/api/shelf-rules/{custom_rule['id']}",
                headers={"X-CSRF-Token":csrf}).status_code, 200)
            saved = client.put("/api/settings", headers={"X-CSRF-Token":csrf}, json={
                "notifications_enabled":"0","notification_time":"18:30"})
            self.assertEqual(saved.status_code, 200)
            settings = client.get("/api/bootstrap").json["settings"]
            self.assertEqual(settings["notifications_enabled"], "0")
            self.assertEqual(settings["notification_time"], "18:30")

            # Lot metadata is editable and the complete previous state is restorable.
            editable = client.post("/api/products", headers={"X-CSRF-Token":csrf}, json={
                "name":"Bewerkbare bak","quantity":1,"unit":"bak","location_id":1,
                "portion_grams":400,"expiry_date":"2026-10-01"}).json
            edited = client.put(f"/api/lots/{editable['lot_id']}",
                headers={"X-CSRF-Token":csrf}, json={"quantity":2,"unit":"bak",
                    "portion_grams":550,"location_id":2,"purchase_date":"2026-09-24",
                    "production_date":"2026-09-23","expiry_date":"2026-12-01",
                    "unit_price":3.5,"store":"Testwinkel"})
            self.assertEqual(edited.status_code, 200)
            changed_lot = client.get(f"/api/products/{editable['id']}").json["lots"][0]
            self.assertEqual(changed_lot["quantity"], 2)
            self.assertEqual(changed_lot["portion_grams"], 550)
            self.assertEqual(changed_lot["location_id"], 2)
            self.assertEqual(client.post(f"/api/history/{edited.json['transaction_id']}/undo",
                headers={"X-CSRF-Token":csrf}, json={}).status_code, 200)
            restored_lot = client.get(f"/api/products/{editable['id']}").json["lots"][0]
            self.assertEqual(restored_lot["quantity"], 1)
            self.assertEqual(restored_lot["portion_grams"], 400)
            self.assertEqual(restored_lot["location_id"], 1)

            # Archiving is non-destructive and preserves product history.
            self.assertEqual(client.delete(f"/api/products/{editable['id']}",
                headers={"X-CSRF-Token":csrf}).status_code, 200)
            self.assertNotIn(editable["id"], [p["id"] for p in client.get("/api/products").json])
            self.assertTrue(any(row["product_id"] == editable["id"]
                                for row in client.get("/api/history").json))
            self.assertEqual(client.post(f"/api/products/{editable['id']}/restore",
                headers={"X-CSRF-Token":csrf}, json={}).status_code, 200)

            # Recipes can be edited and meal planning can add missing ingredients.
            recipe = client.post("/api/recipes", headers={"X-CSRF-Token":csrf}, json={
                "name":"Pasta test","servings":2,"prep_minutes":15,"emoji":"🍝",
                "instructions":"Koken","items":[{"ingredient":"Tomaat",
                    "amount":4,"unit":"stuks"}]}).json
            updated = client.put(f"/api/recipes/{recipe['id']}",
                headers={"X-CSRF-Token":csrf}, json={"name":"Pasta vernieuwd",
                    "servings":2,"prep_minutes":20,"emoji":"🍝","instructions":"20 min koken",
                    "items":[{"ingredient":"Tomaat","amount":6,"unit":"stuks"}]})
            self.assertEqual(updated.status_code, 200)
            self.assertEqual(next(r for r in client.get("/api/recipes").json
                                  if r["id"] == recipe["id"])["name"], "Pasta vernieuwd")
            planned = client.post("/api/meal-plan", headers={"X-CSRF-Token":csrf}, json={
                "plan_date":"2026-09-25","meal":"avondeten","recipe_id":recipe["id"],
                "servings":2,"add_to_shopping":True})
            self.assertEqual(planned.status_code, 201)
            self.assertEqual(planned.json["shopping_added"], 1)
            manual = next(i for i in client.get("/api/shopping").json if not i["automatic"])
            self.assertEqual(client.patch(f"/api/shopping/{manual['id']}",
                headers={"X-CSRF-Token":csrf}, json={"checked":True}).status_code, 204)
            cleared = client.delete("/api/shopping/checked",headers={"X-CSRF-Token":csrf})
            self.assertEqual(cleared.status_code, 200)
            self.assertGreaterEqual(cleared.json["deleted"], 1)
            self.assertTrue(client.get("/api/dashboard").json["locations"])


if __name__ == "__main__":
    unittest.main()
