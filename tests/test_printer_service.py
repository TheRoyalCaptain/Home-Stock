import tempfile
import unittest
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
                    "barcode":"HS-123"}, path)
                self.assertTrue(path.read_bytes().startswith(b"%PDF"))
                self.assertGreater(path.stat().st_size, 1000)

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
