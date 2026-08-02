"""
config.py — Load reference ranges from an external JSON file.

Keeping the BMI categories and CrCl stages in config/reference_ranges.json
lets a user localize or tweak thresholds without touching the code. If the
file is missing or malformed, we fall back to the built-in defaults defined
in calculators.py, so the program always works.

JSON schema (see config/reference_ranges.json):
    {
      "bmi_categories": [[16.0, "Severe thinness"], ..., ["inf", "..."]],
      "crcl_stages":    [[90.0, "Normal ..."], ..., [0.0, "Kidney failure"]]
    }

The string "inf" is accepted for an open-ended upper bound and converted
to float("inf").
"""

import json
import os

import calculators as calc

# Default location: <project_root>/config/reference_ranges.json
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "reference_ranges.json",
)


class ConfigError(Exception):
    """Raised when a config file exists but cannot be parsed into valid ranges."""


def _to_bound(raw):
    """Convert a JSON bound to a float, accepting the string 'inf'."""
    if isinstance(raw, str) and raw.strip().lower() in ("inf", "infinity", "+inf"):
        return float("inf")
    return float(raw)


def _parse_table(raw_table, name):
    """Turn a list of [bound, label] pairs into a tuple of (float, str)."""
    if not isinstance(raw_table, list) or not raw_table:
        raise ConfigError(f"'{name}' must be a non-empty list.")

    table = []
    for pair in raw_table:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ConfigError(f"Each '{name}' entry must be [bound, label].")
        bound, label = pair
        table.append((_to_bound(bound), str(label)))
    return tuple(table)


def load_reference_ranges(path=None):
    """
    Load (bmi_categories, crcl_stages) from a JSON file.

    Returns a dict:
        {"bmi_categories": (...), "crcl_stages": (...), "source": <str>}

    'source' is the file path when loaded from disk, or "defaults" when the
    file is absent. A file that exists but is invalid raises ConfigError so
    the caller can decide whether to warn and continue with defaults.
    """
    target = path or DEFAULT_CONFIG_PATH

    if not os.path.exists(target):
        return {
            "bmi_categories": calc.DEFAULT_BMI_CATEGORIES,
            "crcl_stages": calc.DEFAULT_CRCL_STAGES,
            "source": "defaults",
        }

    try:
        with open(target, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Could not read config: {exc}") from exc

    return {
        "bmi_categories": _parse_table(data.get("bmi_categories"), "bmi_categories"),
        "crcl_stages": _parse_table(data.get("crcl_stages"), "crcl_stages"),
        "source": target,
    }


def apply_reference_ranges(ranges):
    """
    Install loaded ranges as the active tables in calculators.

    Rebinds the module-level tables so all lookup functions pick them up.
    """
    calc.BMI_CATEGORIES = ranges["bmi_categories"]
    calc.CRCL_STAGES = ranges["crcl_stages"]
