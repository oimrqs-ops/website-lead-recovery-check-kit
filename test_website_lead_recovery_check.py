import json
import tempfile
import unittest
from pathlib import Path

from website_lead_recovery_check import audit_html, write_report


GOOD_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <title>Clinic</title>
    <meta name="description" content="desc" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="canonical" href="https://example.com" />
  </head>
  <body>
    <a href="mailto:hello@example.com">Email</a>
    <a href="tel:+15550001">Call</a>
    <a href="https://wa.me/15550001">WhatsApp</a>
    <a href="/contact">Contact</a>
    <a href="/book">Book now</a>
    <button>Book appointment</button>
    <form action="/lead" method="post"></form>
  </body>
</html>
"""


class LeadRecoveryCheckTests(unittest.TestCase):
    def test_audit_passes_core_paths(self):
        report = audit_html(GOOD_HTML, "inline")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["summary"]["warnings"], 0)

    def test_audit_flags_missing_items(self):
        report = audit_html("<html><head><title>X</title></head><body></body></html>", "inline")
        self.assertGreaterEqual(report["summary"]["failed"], 4)

    def test_write_report_outputs_files(self):
        report = audit_html(GOOD_HTML, "inline")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_report(report, out)
            self.assertTrue((out / "lead-recovery-report.md").exists())
            self.assertTrue((out / "lead-recovery-summary.json").exists())
            data = json.loads((out / "lead-recovery-summary.json").read_text())
            self.assertEqual(data["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
