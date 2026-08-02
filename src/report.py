"""
report.py — Build and save a plain-text session report for VitalScope.

The report is deliberately color-free (no ANSI codes) so the saved file
is clean when opened in any editor. Reports are written to a `reports/`
directory next to the project, with a timestamped filename.

A history entry is a dict:
    {"time": "2026-08-02 14:33:05", "summary": "BMI: 22.9 kg/m^2 (Normal weight)"}
"""

import os
from datetime import datetime

# Directory where reports are saved (created on demand).
REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"
)

_DISCLAIMER = (
    "DISCLAIMER: Educational use only. Not a medical device. "
    "Do not use for diagnosis or treatment."
)


def build_report(history, generated_at=None):
    """
    Return the full report text for a list of history entries.

    `generated_at` is an optional datetime (mainly for testing); when
    omitted the current time is used.
    """
    when = generated_at or datetime.now()
    stamp = when.strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("=" * 52)
    lines.append("  VitalScope — Clinical Health Metrics Report")
    lines.append("=" * 52)
    lines.append(f"Generated: {stamp}")
    lines.append(f"Calculations: {len(history)}")
    lines.append("")
    lines.append("-" * 52)

    if history:
        for i, entry in enumerate(history, start=1):
            lines.append(f"{i}. [{entry['time']}] {entry['summary']}")
    else:
        lines.append("(no calculations performed)")

    lines.append("-" * 52)
    lines.append("")
    lines.append(_DISCLAIMER)
    lines.append("")

    # Trailing newline so the file ends cleanly.
    return "\n".join(lines) + "\n"


def default_report_path(generated_at=None):
    """Build a timestamped path like reports/vitalscope_20260802_143305.txt."""
    when = generated_at or datetime.now()
    filename = when.strftime("vitalscope_%Y%m%d_%H%M%S.txt")
    return os.path.join(REPORTS_DIR, filename)


def save_report(history, path=None, generated_at=None):
    """
    Write the report to `path` (or a default timestamped path) and return
    the path that was written. Creates the reports/ directory if needed.
    """
    when = generated_at or datetime.now()
    target = path or default_report_path(when)

    os.makedirs(os.path.dirname(target), exist_ok=True)
    text = build_report(history, generated_at=when)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(text)
    return target
