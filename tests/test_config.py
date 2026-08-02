"""
test_config.py — Tests for loading reference ranges from JSON.

Run with:
    python -m pytest tests/
or:
    python -m unittest discover -s tests
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import calculators as calc  # noqa: E402
import config  # noqa: E402


def write_json(directory, name, data):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    return path


class TestLoadReferenceRanges(unittest.TestCase):
    def test_missing_file_uses_defaults(self):
        ranges = config.load_reference_ranges(path="does_not_exist.json")
        self.assertEqual(ranges["source"], "defaults")
        self.assertEqual(ranges["bmi_categories"], calc.DEFAULT_BMI_CATEGORIES)

    def test_inf_string_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(tmp, "ranges.json", {
                "bmi_categories": [[25.0, "Normal-ish"], ["inf", "High"]],
                "crcl_stages": [[0.0, "All"]],
            })
            ranges = config.load_reference_ranges(path=path)
            # Last BMI bound must become math infinity.
            self.assertEqual(ranges["bmi_categories"][-1][0], float("inf"))
            self.assertEqual(ranges["bmi_categories"][-1][1], "High")

    def test_custom_thresholds_affect_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            # A deliberately silly table: everything under 100 is "Low".
            path = write_json(tmp, "ranges.json", {
                "bmi_categories": [[100.0, "Low"], ["inf", "High"]],
                "crcl_stages": [[0.0, "Any"]],
            })
            ranges = config.load_reference_ranges(path=path)
            self.assertEqual(
                calc.bmi_category(22.0, categories=ranges["bmi_categories"]),
                "Low",
            )

    def test_malformed_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{ not valid json ")
            with self.assertRaises(config.ConfigError):
                config.load_reference_ranges(path=path)

    def test_bad_shape_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(tmp, "ranges.json", {
                "bmi_categories": "not-a-list",
                "crcl_stages": [[0.0, "Any"]],
            })
            with self.assertRaises(config.ConfigError):
                config.load_reference_ranges(path=path)


class TestApplyReferenceRanges(unittest.TestCase):
    def setUp(self):
        # Snapshot the active tables so we can restore them after the test.
        self._bmi = calc.BMI_CATEGORIES
        self._crcl = calc.CRCL_STAGES

    def tearDown(self):
        calc.BMI_CATEGORIES = self._bmi
        calc.CRCL_STAGES = self._crcl

    def test_apply_rebinds_active_tables(self):
        ranges = {
            "bmi_categories": ((100.0, "Low"), (float("inf"), "High")),
            "crcl_stages": ((0.0, "Any"),),
            "source": "test",
        }
        config.apply_reference_ranges(ranges)
        # bmi_category with no explicit table now uses the applied one.
        self.assertEqual(calc.bmi_category(22.0), "Low")


if __name__ == "__main__":
    unittest.main()
