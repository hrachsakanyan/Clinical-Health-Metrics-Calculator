"""
calculators.py — Clinical health metric calculations for VitalScope.

Each calculator is a small, pure function that takes validated numeric
inputs and returns a result. Interpretation/category lookups are kept
separate from the raw math so the formulas stay easy to read and test.

All formulas use metric units internally:
    - weight in kilograms (kg)
    - height in centimeters (cm)
    - age in years

Unit conversion for imperial input happens in the CLI layer (main.py),
so these functions always receive metric values.

DISCLAIMER: Educational use only. Not for clinical decision-making.
"""

# ---------------------------------------------------------------------------
# Lookup tables (reference ranges / categories)
# ---------------------------------------------------------------------------

# WHO BMI categories. Each tuple is (upper_bound_exclusive, label).
# The last entry uses float("inf") to catch everything above the range.
DEFAULT_BMI_CATEGORIES = (
    (16.0, "Severe thinness"),
    (17.0, "Moderate thinness"),
    (18.5, "Mild thinness"),
    (25.0, "Normal weight"),
    (30.0, "Overweight"),
    (35.0, "Obese (Class I)"),
    (40.0, "Obese (Class II)"),
    (float("inf"), "Obese (Class III)"),
)

# Cockcroft-Gault kidney function stages, based on creatinine clearance
# (mL/min). Tuple is (lower_bound_inclusive, label).
DEFAULT_CRCL_STAGES = (
    (90.0, "Normal / high kidney function"),
    (60.0, "Mildly reduced kidney function"),
    (30.0, "Moderately reduced kidney function"),
    (15.0, "Severely reduced kidney function"),
    (0.0, "Kidney failure"),
)

# "Active" tables used by the lookup functions. These start as the built-in
# defaults but may be replaced at startup by config.load_reference_ranges()
# (see config.py). Functions read these module globals by name, so rebinding
# them here takes effect everywhere.
BMI_CATEGORIES = DEFAULT_BMI_CATEGORIES
CRCL_STAGES = DEFAULT_CRCL_STAGES


# ---------------------------------------------------------------------------
# Core calculators
# ---------------------------------------------------------------------------

def bmi(weight_kg, height_cm):
    """Body Mass Index = weight(kg) / height(m)^2."""
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2)


def bmi_category(value, categories=None):
    """
    Return the WHO category label for a BMI value.

    `categories` lets a caller (or test) pass a custom table; when omitted
    the active module-level BMI_CATEGORIES is used.
    """
    table = categories if categories is not None else BMI_CATEGORIES
    for upper_bound, label in table:
        if value < upper_bound:
            return label
    # Unreachable when the table ends with inf, but safe as a fallback.
    return "Unknown"


def bsa_mosteller(weight_kg, height_cm):
    """
    Body Surface Area (m^2), Mosteller formula:
        BSA = sqrt((height_cm * weight_kg) / 3600)
    """
    return ((height_cm * weight_kg) / 3600.0) ** 0.5


def bmr_mifflin_st_jeor(weight_kg, height_cm, age_years, sex):
    """
    Basal Metabolic Rate (kcal/day), Mifflin-St Jeor equation:
        male:   10*kg + 6.25*cm - 5*age + 5
        female: 10*kg + 6.25*cm - 5*age - 161
    'sex' is 'male' or 'female'.
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age_years)
    if sex == "male":
        return base + 5.0
    return base - 161.0


def ideal_body_weight_devine(height_cm, sex):
    """
    Ideal Body Weight (kg), Devine formula. Defined for height >= 152.4 cm
    (60 inches); below that the base value is returned.
        male:   50.0 kg + 2.3 kg per inch over 60 inches
        female: 45.5 kg + 2.3 kg per inch over 60 inches
    """
    inches_over_60 = max(0.0, (height_cm / 2.54) - 60.0)
    base = 50.0 if sex == "male" else 45.5
    return base + (2.3 * inches_over_60)


def creatinine_clearance_cockcroft_gault(weight_kg, age_years, serum_cr_mg_dl, sex):
    """
    Creatinine Clearance (mL/min), Cockcroft-Gault equation:
        CrCl = ((140 - age) * weight_kg * sex_factor) / (72 * serum_Cr)
        sex_factor = 0.85 for female, 1.0 for male
    serum_cr_mg_dl is serum creatinine in mg/dL.
    """
    sex_factor = 1.0 if sex == "male" else 0.85
    return ((140.0 - age_years) * weight_kg * sex_factor) / (72.0 * serum_cr_mg_dl)


def crcl_stage(value, stages=None):
    """
    Return a kidney-function stage label for a creatinine clearance value.

    `stages` lets a caller (or test) pass a custom table; when omitted the
    active module-level CRCL_STAGES is used.
    """
    table = stages if stages is not None else CRCL_STAGES
    for lower_bound, label in table:
        if value >= lower_bound:
            return label
    return "Unknown"


# ---------------------------------------------------------------------------
# Severity classification (for color coding in the CLI)
# ---------------------------------------------------------------------------
# These map a raw value to one of "good" / "warn" / "bad" so the display
# layer can color it without knowing any medical thresholds itself.

def bmi_severity(value):
    """Severity of a BMI value: normal is good, edges are warn/bad."""
    if 18.5 <= value < 25.0:
        return "good"
    if 17.0 <= value < 18.5 or 25.0 <= value < 30.0:
        return "warn"
    return "bad"


def crcl_severity(value):
    """Severity of a creatinine clearance value (mL/min)."""
    if value >= 90.0:
        return "good"
    if value >= 60.0:
        return "warn"
    return "bad"


# ---------------------------------------------------------------------------
# Unit conversion helpers (used by the CLI for imperial input)
# ---------------------------------------------------------------------------

def lb_to_kg(pounds):
    """Convert pounds to kilograms."""
    return pounds * 0.45359237


def inch_to_cm(inches):
    """Convert inches to centimeters."""
    return inches * 2.54
