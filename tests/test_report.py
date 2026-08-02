"""
test_report.py — Unit tests for the .txt report builder/saver.

Run with:
    python -m pytest tests/
or:
    python -m unittest discover -s tests
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import report  # noqa: E402


SAMPLE_HISTORY = [
    {"time": "2026-08-02 14:33:05", "summary": "BMI: 22.9 kg/m^2 (Normal weight)"},
    {"time": "2026-08-02 14:34:10", "summary": "BSA (Mosteller): 1.84 m^2"},
]

FIXED_TIME = datetime(2026, 8, 2, 14, 35, 0)


class TestBuildReport(unittest.TestCase):
    def test_contains_entries_and_header(self):
        text = report.build_report(SAMPLE_HISTORY, generated_at=FIXED_TIME)
        self.assertIn("VitalScope", text)
        self.assertIn("Generated: 2026-08-02 14:35:00", text)
        self.assertIn("Calculations: 2", text)
        self.assertIn("BMI: 22.9 kg/m^2 (Normal weight)", text)
        self.assertIn("BSA (Mosteller): 1.84 m^2", text)

    def test_numbered_and_disclaimer(self):
        text = report.build_report(SAMPLE_HISTORY, generated_at=FIXED_TIME)
        self.assertIn("1. [2026-08-02 14:33:05]", text)
        self.assertIn("2. [2026-08-02 14:34:10]", text)
        self.assertIn("DISCLAIMER", text)

    def test_empty_history(self):
        text = report.build_report([], generated_at=FIXED_TIME)
        self.assertIn("Calculations: 0", text)
        self.assertIn("(no calculations performed)", text)

    def test_no_ansi_codes(self):
        # Report text must be plain — no color escape sequences.
        text = report.build_report(SAMPLE_HISTORY, generated_at=FIXED_TIME)
        self.assertNotIn("\x1b[", text)


class TestSaveReport(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out", "session.txt")
            written = report.save_report(SAMPLE_HISTORY, path=path,
                                         generated_at=FIXED_TIME)
            self.assertEqual(written, path)
            self.assertTrue(os.path.exists(path))
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("BMI: 22.9 kg/m^2 (Normal weight)", content)

    def test_default_path_is_timestamped(self):
        path = report.default_report_path(generated_at=FIXED_TIME)
        self.assertTrue(path.endswith("vitalscope_20260802_143500.txt"))


if __name__ == "__main__":
    unittest.main()
