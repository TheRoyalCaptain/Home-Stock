import tempfile
import unittest
import re
from pathlib import Path
from unittest.mock import patch

import printer_service


class PrinterServiceTest(unittest.TestCase):
    def test_generates_real_pdf_in_both_sizes(self):
        with tempfile.TemporaryDirectory() as folder:
            for size in ("57x32", "101x54"):
                path = Path(folder) / f"{size}.pdf"
                printer_service.label_pdf({"label_size":size,"name":"Melk",
                    "detail":"1 liter · THT 2026-09-30","footer":"Koelkast · HS-123",
                    "barcode":"HS-123","short_code":"ME001","location":"Koelkast",
                    "contents":"Halfvolle melk","production_date":"2026-09-21",
                    "preparation_instructions":"Koel serveren en voor gebruik schudden.",
                    "expiry_date":"2026-09-30","placed_by":"Kevin"}, path)
                data=path.read_bytes()
                self.assertTrue(data.startswith(b"%PDF"))
                self.assertGreater(path.stat().st_size, 1000)
                if size=="101x54":
                    self.assertRegex(data,br"/MediaBox\s*\[\s*0\s+0\s+153[^]]+286")

    def test_dutch_label_date(self):
        self.assertEqual(printer_service.label_date("2026-07-20"),"20 JUL 2026")

    def test_detects_only_supported_usb_dymo(self):
        output = """direct usb://DYMO/LabelWriter%20450?serial=ABC
direct usb://DYMO/LabelWriter%20550?serial=NOPE
network ipp://printer.local/ipp/print
"""
        with patch.object(printer_service, "run") as run:
            run.return_value.stdout = output
            self.assertEqual(printer_service.detected_devices(),
                ["usb://DYMO/LabelWriter%20450?serial=ABC"])


if __name__ == "__main__":
    unittest.main()
