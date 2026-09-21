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


def label_date(value):
    if not value:return "—"
    try:
        year,month,day=str(value).split("-")[:3]
        months=["JAN","FEB","MRT","APR","MEI","JUN","JUL","AUG","SEP","OKT","NOV","DEC"]
        return f"{int(day):02d} {months[int(month)-1]} {year}"
    except (ValueError,IndexError):return safe_text(value,20)


def wrapped(canvas, text, x, y, max_width, font="Helvetica", size=7, lines=3, leading=None):
    words=safe_text(text,240).split();rows=[];current=""
    for word in words:
        candidate=(current+" "+word).strip()
        if canvas.stringWidth(candidate,font,size)<=max_width:current=candidate
        else:
            if current:rows.append(current)
            current=word
            if len(rows)>=lines:break
    if current and len(rows)<lines:rows.append(current)
    leading=leading or size*1.2
    canvas.setFont(font,size)
    for index,row in enumerate(rows):canvas.drawString(x,y-index*leading,row)
    return rows


def label_pdf(data, path):
    sizes = {"57x32": (57*mm, 32*mm), "101x54": (54*mm, 101*mm)}
    width, height = sizes.get(data.get("label_size"), sizes["57x32"])
    canvas = Canvas(str(path), pagesize=(width, height), pageCompression=1)
    margin=2.3*mm;name=safe_text(data.get("name"),70)
    value=safe_text(data.get("barcode"),80) or "HOME-STOCK"
    if data.get("label_size")=="101x54":
        location=safe_text(data.get("location") or "ONBEKENDE LOCATIE",30).upper()
        kind="ZELFGEMAAKT" if data.get("product_type")=="homemade" else "WINKELPRODUCT"
        canvas.setFillColorRGB(0,0,0);canvas.roundRect(margin,height-margin-18,width-2*margin,18,3,fill=1,stroke=0)
        canvas.setFillColorRGB(1,1,1);canvas.setFont("Helvetica-Bold",7);canvas.drawString(margin+5,height-margin-11,location)
        canvas.setFont("Helvetica",5);canvas.drawRightString(width-margin-5,height-margin-11,kind)
        canvas.setFillColorRGB(0,0,0)
        wrapped(canvas,name,margin,height-margin-32,width-2*margin,"Helvetica-Bold",11,2,12)
        canvas.setFont("Helvetica-Bold",22);canvas.drawCentredString(width/2,height-margin-76,safe_text(data.get("lot_code") or data.get("short_code"),12))
        barcode=code128.Code128(value,barHeight=10*mm,barWidth=.22*mm,humanReadable=False)
        scale=min(1,(width-2*margin)/barcode.width);canvas.saveState();canvas.translate(margin,height-margin-112);canvas.scale(scale,1);barcode.drawOn(canvas,0,0);canvas.restoreState()
        canvas.setFont("Helvetica-Bold",5.5);canvas.drawString(margin,height-margin-122,"INHOUD / INGREDIËNTEN")
        wrapped(canvas,data.get("contents") or name,margin,height-margin-132,width-2*margin,"Helvetica",7,3,8)
        box_y=31*mm;box_h=12*mm;gap=1.5*mm;box_w=(width-2*margin-gap)/2
        production=data.get("production_date") or data.get("purchase_date")
        production_title=("BEREID" if data.get("product_type")=="homemade" else "GEPRODUCEERD") if data.get("production_date") else "INGELEGD"
        for x,title,value_date in ((margin,production_title,production),(margin+box_w+gap,"EINDDATUM",data.get("expiry_date"))):
            canvas.roundRect(x,box_y,box_w,box_h,3,fill=0,stroke=1);canvas.setFont("Helvetica-Bold",5.5);canvas.drawString(x+4,box_y+box_h-8,title);canvas.setFont("Helvetica-Bold",7);canvas.drawString(x+4,box_y+7,label_date(value_date))
        canvas.setFont("Helvetica-Bold",5.5);canvas.drawString(margin,24*mm,"INGELEGD DOOR "+safe_text(data.get("placed_by") or "ONBEKEND",24).upper())
        canvas.drawRightString(width-margin,24*mm,safe_text(data.get("detail"),30))
        canvas.line(margin,21.5*mm,width-margin,21.5*mm)
        descriptor=" · ".join(x for x in (safe_text(data.get("brand"),25),safe_text(data.get("category"),25)) if x)
        canvas.setFont("Helvetica-Bold",5.5);canvas.drawString(margin,16.5*mm,"PRODUCTINFORMATIE")
        canvas.setFont("Helvetica",6.5);canvas.drawString(margin,13*mm,descriptor or kind.title())
        canvas.setFont("Helvetica-Bold",5.5);canvas.drawString(margin,7.5*mm,"PARTIJ")
        canvas.setFont("Helvetica",6.5);canvas.drawRightString(width-margin,7.5*mm,safe_text(data.get("footer"),60))
        canvas.setFont("Helvetica",4.5);canvas.drawCentredString(width/2,2*mm,"HOME STOCK · BEWAARETIKET")
    else:
        canvas.setFont("Helvetica-Bold",9);canvas.drawString(margin,height-margin-7,name)
        canvas.setFont("Helvetica-Bold",13);canvas.drawRightString(width-margin,height-margin-18,safe_text(data.get("lot_code") or data.get("short_code"),12))
        barcode=code128.Code128(value,barHeight=8*mm,barWidth=.21*mm,humanReadable=False)
        scale=min(1,(width-2*margin)/barcode.width);canvas.saveState();canvas.translate(margin,4*mm);canvas.scale(scale,1);barcode.drawOn(canvas,0,0);canvas.restoreState()
        canvas.setFont("Helvetica",5);canvas.drawRightString(width-margin,1.5*mm,safe_text(data.get("footer"),60))
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
        width,height=("54","101") if size=="101x54" else ("57","32")
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
