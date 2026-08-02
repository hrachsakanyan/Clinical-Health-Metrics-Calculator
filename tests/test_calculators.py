"""
test_calculators.py — Unit tests for VitalScope formulas.

Run with:
    python -m pytest tests/
or with the standard library only:
    python -m unittest discover -s tests

The imports below add src/ to the path so the module can be found
whether you run pytest from the project root or the tests directory.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import calculators as calc  # noqa: E402


class TestBMI(unittest.TestCase):
    def test_normal_value(self):
        # 70 kg, 175 cm -> 22.857...
        self.assertAlmostEqual(calc.bmi(70, 175), 22.857, places=2)

    def test_categories(self):
        self.assertEqual(calc.bmi_category(15.0), "Severe thinness")
        self.assertEqual(calc.bmi_category(22.0), "Normal weight")
        self.assertEqual(calc.bmi_category(27.0), "Overweight")
        self.assertEqual(calc.bmi_category(45.0), "Obese (Class III)")

    def test_boundary_is_lower_category(self):
        # Exactly 25.0 is not < 25.0, so it falls into Overweight.
        self.assertEqual(calc.bmi_category(25.0), "Overweight")
        # Exactly 24.9 is still Normal.
        self.assertEqual(calc.bmi_category(24.9), "Normal weight")


class TestBSA(unittest.TestCase):
    def test_mosteller(self):
        # 70 kg, 175 cm -> sqrt(70*175/3600) = sqrt(3.4028) = 1.8447
        self.assertAlmostEqual(calc.bsa_mosteller(70, 175), 1.8447, places=3)


class TestBMR(unittest.TestCase):
    def test_male(self):
        # 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
        self.assertAlmostEqual(calc.bmr_mifflin_st_jeor(80, 180, 30, "male"), 1780.0)

    def test_female(self):
        # 10*60 + 6.25*165 - 5*30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
        self.assertAlmostEqual(
            calc.bmr_mifflin_st_jeor(60, 165, 30, "female"), 1320.25
        )


class TestIdealBodyWeight(unittest.TestCase):
    def test_male_at_60_inches(self):
        # 152.4 cm == 60 inches -> exactly the base 50.0
        self.assertAlmostEqual(calc.ideal_body_weight_devine(152.4, "male"), 50.0)

    def test_female_taller(self):
        # 165.1 cm == 65 inches -> 45.5 + 2.3*5 = 57.0
        self.assertAlmostEqual(
            calc.ideal_body_weight_devine(165.1, "female"), 57.0, places=1
        )

    def test_below_minimum_height_uses_base(self):
        # Below 60 inches, inches_over_60 clamps to 0 -> base value.
        self.assertAlmostEqual(calc.ideal_body_weight_devine(140, "male"), 50.0)


class TestCreatinineClearance(unittest.TestCase):
    def test_male(self):
        # ((140-40)*80*1.0) / (72*1.0) = 8000/72 = 111.11
        result = calc.creatinine_clearance_cockcroft_gault(80, 40, 1.0, "male")
        self.assertAlmostEqual(result, 111.11, places=2)

    def test_female_factor(self):
        # Female applies 0.85 multiplier.
        male = calc.creatinine_clearance_cockcroft_gault(80, 40, 1.0, "male")
        female = calc.creatinine_clearance_cockcroft_gault(80, 40, 1.0, "female")
        self.assertAlmostEqual(female, male * 0.85, places=5)

    def test_stages(self):
        self.assertEqual(calc.crcl_stage(120), "Normal / high kidney function")
        self.assertEqual(calc.crcl_stage(75), "Mildly reduced kidney function")
        self.assertEqual(calc.crcl_stage(45), "Moderately reduced kidney function")
        self.assertEqual(calc.crcl_stage(20), "Severely reduced kidney function")
        self.assertEqual(calc.crcl_stage(10), "Kidney failure")


class TestSeverity(unittest.TestCase):
    def test_bmi_severity(self):
        self.assertEqual(calc.bmi_severity(22.0), "good")
        self.assertEqual(calc.bmi_severity(27.0), "warn")   # overweight
        self.assertEqual(calc.bmi_severity(18.0), "warn")   # mild thinness
        self.assertEqual(calc.bmi_severity(32.0), "bad")    # obese
        self.assertEqual(calc.bmi_severity(16.0), "bad")    # severe thinness

    def test_crcl_severity(self):
        self.assertEqual(calc.crcl_severity(95), "good")
        self.assertEqual(calc.crcl_severity(70), "warn")
        self.assertEqual(calc.crcl_severity(40), "bad")


class TestConversions(unittest.TestCase):
    def test_lb_to_kg(self):
        self.assertAlmostEqual(calc.lb_to_kg(154.324), 70.0, places=2)

    def test_inch_to_cm(self):
        self.assertAlmostEqual(calc.inch_to_cm(60), 152.4, places=1)


if __name__ == "__main__":
    unittest.main()
