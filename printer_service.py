"""Internal USB/CUPS service for DYMO LabelWriter 400 and 450 printers."""
import os
import re
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

app = Flask(__name__)
SUPPORTED = re.compile(r"dymo.*labelwriter.*(?:400|450)", re.I)


def run(*args, timeout=20):
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout)


def detected_devices():
    result = run("lpinfo", "-v")
    devices = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[0] == "direct" and SUPPORTED.search(parts[1].replace("%20", " ")):
            devices.append(parts[1])
    return devices


def model_driver(uri):
    text = uri.replace("%20", " ")
    wanted = "450" if "450" in text else "400"
    result = run("lpinfo", "-m")
    rows = [line for line in result.stdout.splitlines() if "dymo" in line.lower()]
    for line in rows:
        if wanted in line and "labelwriter" in line.lower():
            return line.split(maxsplit=1)[0]
    for line in rows:
        if "labelwriter" in line.lower():
            return line.split(maxsplit=1)[0]
    raise RuntimeError("De DYMO CUPS-driver is niet gevonden")


def queue_name(uri):
    model = "450" if "450" in uri.replace("%20", " ") else "400"
    return "Home_Stock_DYMO_" + model


def ensure_printers():
    found = []
    for uri in detected_devices():
        name = queue_name(uri)
        result = run("lpstat", "-p", name)
        if result.returncode != 0:
            added = run("lpadmin", "-p", name, "-E", "-v", uri, "-m", model_driver(uri))
            if added.returncode != 0:
                raise RuntimeError(added.stderr.strip() or "Printer kon niet worden toegevoegd")
        run("cupsenable", name)
        run("cupsaccept", name)
        status = run("lpstat", "-p", name).stdout.strip()
        found.append({"id": name, "name": name.replace("_", " "), "uri": uri,
                      "model": "DYMO LabelWriter " + ("450" if "450" in name else "400"),
                      "status": status or "beschikbaar"})
    return found


def safe_text(value, limit):
    return str(value or "").replace("\n", " ").strip()[:limit]


def label_pdf(data, path):
    sizes = {"57x32": (57*mm, 32*mm), "101x54": (101*mm, 54*mm)}
    width, height = sizes.get(data.get("label_size"), sizes["57x32"])
    canvas = Canvas(str(path), pagesize=(width, height), pageCompression=1)
    margin = 2.2*mm
    name = safe_text(data.get("name"), 55)
    detail = safe_text(data.get("detail"), 70)
    footer = safe_text(data.get("footer"), 70)
    value = safe_text(data.get("barcode"), 80) or "HOME-STOCK"
    canvas.setFont("Helvetica-Bold", 10 if width < 80*mm else 14)
    canvas.drawString(margin, height-margin-8, name)
    canvas.setFont("Helvetica", 7 if width < 80*mm else 10)
    canvas.drawString(margin, height-margin-18, detail)
    barcode = code128.Code128(value, barHeight=9*mm if height < 40*mm else 17*mm,
                              barWidth=.23*mm, humanReadable=True)
    scale = min(1, (width-2*margin) / barcode.width)
    canvas.saveState()
    canvas.translate(margin, 3.5*mm)
    canvas.scale(scale, 1)
    barcode.drawOn(canvas, 0, 0)
    canvas.restoreState()
    canvas.setFont("Helvetica", 5.5 if width < 80*mm else 8)
    canvas.drawRightString(width-margin, 1.5*mm, footer)
    canvas.showPage()
    canvas.save()


def submit(data):
    printers = ensure_printers()
    requested = safe_text(data.get("printer"), 100)
    printer = next((p for p in printers if p["id"] == requested), None) if requested else None
    printer = printer or (printers[0] if printers else None)
    if not printer:
        raise RuntimeError("Geen ondersteunde DYMO LabelWriter 400/450 gevonden via USB")
    copies = max(1, min(int(data.get("copies") or 1), 99))
    size = data.get("label_size") if data.get("label_size") in {"57x32", "101x54"} else "57x32"
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "home-stock-label.pdf"
        label_pdf({**data, "label_size": size}, path)
        width, height = size.split("x")
        result = run("lp", "-d", printer["id"], "-n", str(copies),
                     "-o", f"media=Custom.{width}x{height}mm", "-o", "fit-to-page",
                     "-t", "Home Stock label", str(path), timeout=30)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "CUPS heeft de printopdracht geweigerd")
    return {"printer": printer, "job": result.stdout.strip(), "copies": copies}


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/printers")
def printers():
    try:
        return jsonify(printers=ensure_printers())
    except Exception as error:
        return jsonify(printers=[], error=str(error)), 503


@app.post("/print")
def print_label():
    try:
        return jsonify(ok=True, **submit(request.get_json(silent=True) or {}))
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        return jsonify(error=str(error)), 503


@app.post("/test")
def test_label():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(ok=True, **submit({**data, "name":"Home Stock",
            "detail":"DYMO-testlabel · direct vanaf de server",
            "footer":"Printer correct ingesteld", "barcode":"HOME-STOCK-TEST", "copies":1}))
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        return jsonify(error=str(error)), 503
