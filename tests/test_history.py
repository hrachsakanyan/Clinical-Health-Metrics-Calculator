"""
test_history.py — Tests for persistent JSONL session history.

Run with:
    python -m pytest tests/
or:
    python -m unittest discover -s tests
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import history  # noqa: E402


ENTRY_A = {"time": "2026-08-02 14:33:05", "summary": "BMI: 22.9 kg/m^2 (Normal)"}
ENTRY_B = {"time": "2026-08-02 14:34:10", "summary": "BSA (Mosteller): 1.84 m^2"}


class TestHistory(unittest.TestCase):
    def test_missing_file_returns_empty(self):
        self.assertEqual(history.load_history(path="nope.jsonl"), [])

    def test_append_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data", "history.jsonl")
            history.append_entry(ENTRY_A, path=path)
            history.append_entry(ENTRY_B, path=path)
            records = history.load_history(path=path)
            self.assertEqual(records, [ENTRY_A, ENTRY_B])

    def test_corrupt_line_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "history.jsonl")
            history.append_entry(ENTRY_A, path=path)
            # Inject a broken line between valid ones.
            with open(path, "a", encoding="utf-8") as handle:
                handle.write("this is not json\n")
            history.append_entry(ENTRY_B, path=path)
            records = history.load_history(path=path)
            self.assertEqual(records, [ENTRY_A, ENTRY_B])

    def test_clear_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "history.jsonl")
            history.append_entry(ENTRY_A, path=path)
            self.assertTrue(history.clear_history(path=path))
            self.assertFalse(os.path.exists(path))
            # Clearing again reports nothing to remove.
            self.assertFalse(history.clear_history(path=path))

    def test_unicode_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "history.jsonl")
            entry = {"time": "t", "summary": "Քաշ՝ նորմալ"}
            history.append_entry(entry, path=path)
            self.assertEqual(history.load_history(path=path), [entry])


if __name__ == "__main__":
    unittest.main()
