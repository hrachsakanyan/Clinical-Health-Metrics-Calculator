"""
main.py — Menu-based CLI for VitalScope.

Wraps the pure functions in calculators.py with:
    - a simple text menu,
    - robust input validation (numbers, ranges, choices),
    - unit selection (metric / imperial),
    - categorized output with short interpretations.

Run:
    python src/main.py

DISCLAIMER: Educational use only. Not for clinical decision-making.
"""

from datetime import datetime

import calculators as calc
import config
import history as history_store
import report
from colors import c


# Map a severity string ("good"/"warn"/"bad") to the matching color helper.
SEVERITY_COLORS = {
    "good": c.good,
    "warn": c.warn,
    "bad": c.bad,
}


def paint_severity(text, severity):
    """Color `text` according to a severity level, defaulting to plain."""
    painter = SEVERITY_COLORS.get(severity, lambda t: t)
    return painter(text)


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def read_float(prompt, minimum=None, maximum=None):
    """
    Prompt until the user enters a valid float within [minimum, maximum].
    Bounds are optional. Keeps asking on invalid input instead of crashing.
    """
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print(c.error("  ! Please enter a valid number (e.g. 70.5)."))
            continue

        if minimum is not None and value < minimum:
            print(c.error(f"  ! Value must be >= {minimum}."))
            continue
        if maximum is not None and value > maximum:
            print(c.error(f"  ! Value must be <= {maximum}."))
            continue
        return value


def read_choice(prompt, choices):
    """
    Prompt until the user enters one of the allowed choices.
    'choices' is a dict mapping accepted input -> canonical value,
    e.g. {"m": "male", "f": "female"}. Matching is case-insensitive.
    """
    while True:
        raw = input(prompt).strip().lower()
        if raw in choices:
            return choices[raw]
        print(c.error(f"  ! Please choose one of: {', '.join(choices)}."))


def read_sex():
    """Ask for biological sex (needed by several formulas)."""
    return read_choice("Sex [m/f]: ", {"m": "male", "f": "female"})


# ---------------------------------------------------------------------------
# Unit handling
# ---------------------------------------------------------------------------

def read_weight_kg(unit):
    """Read weight in the chosen unit and return kilograms."""
    if unit == "imperial":
        pounds = read_float("Weight (lb): ", minimum=1, maximum=1000)
        return calc.lb_to_kg(pounds)
    return read_float("Weight (kg): ", minimum=1, maximum=500)


def read_height_cm(unit):
    """Read height in the chosen unit and return centimeters."""
    if unit == "imperial":
        inches = read_float("Height (in): ", minimum=20, maximum=100)
        return calc.inch_to_cm(inches)
    return read_float("Height (cm): ", minimum=50, maximum=260)


def choose_units():
    """Ask once whether the session uses metric or imperial units."""
    return read_choice(
        "Units [m = metric, i = imperial]: ",
        {"m": "metric", "i": "imperial"},
    )


# ---------------------------------------------------------------------------
# Calculation flows (one per menu item)
# ---------------------------------------------------------------------------

def flow_bmi(unit):
    weight = read_weight_kg(unit)
    height = read_height_cm(unit)
    value = calc.bmi(weight, height)
    category = calc.bmi_category(value)
    severity = calc.bmi_severity(value)
    print(f"\n  {c.label('BMI:')} {c.value(f'{value:.1f} kg/m^2')}")
    print(f"  {c.label('Category:')} {paint_severity(category, severity)}")
    return f"BMI: {value:.1f} kg/m^2 ({category})"


def flow_bsa(unit):
    weight = read_weight_kg(unit)
    height = read_height_cm(unit)
    value = calc.bsa_mosteller(weight, height)
    print(f"\n  {c.label('BSA (Mosteller):')} {c.value(f'{value:.2f} m^2')}")
    return f"BSA (Mosteller): {value:.2f} m^2"


def flow_bmr(unit):
    weight = read_weight_kg(unit)
    height = read_height_cm(unit)
    age = read_float("Age (years): ", minimum=1, maximum=120)
    sex = read_sex()
    value = calc.bmr_mifflin_st_jeor(weight, height, age, sex)
    print(f"\n  {c.label('BMR (Mifflin-St Jeor):')} {c.value(f'{value:.0f} kcal/day')}")
    print(c.dim("  Interpretation: energy your body uses at complete rest."))
    return f"BMR: {value:.0f} kcal/day"


def flow_ibw(unit):
    height = read_height_cm(unit)
    sex = read_sex()
    value = calc.ideal_body_weight_devine(height, sex)
    print(f"\n  {c.label('Ideal Body Weight (Devine):')} {c.value(f'{value:.1f} kg')}")
    return f"Ideal Body Weight (Devine): {value:.1f} kg"


def flow_crcl(unit):
    weight = read_weight_kg(unit)
    age = read_float("Age (years): ", minimum=1, maximum=120)
    serum_cr = read_float("Serum creatinine (mg/dL): ", minimum=0.1, maximum=20)
    sex = read_sex()
    value = calc.creatinine_clearance_cockcroft_gault(weight, age, serum_cr, sex)
    stage = calc.crcl_stage(value)
    severity = calc.crcl_severity(value)
    label = c.label("Creatinine Clearance (Cockcroft-Gault):")
    print(f"\n  {label} {c.value(f'{value:.1f} mL/min')}")
    print(f"  {c.label('Stage:')} {paint_severity(stage, severity)}")
    return f"CrCl: {value:.1f} mL/min ({stage})"


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

MENU = (
    ("1", "BMI  — Body Mass Index", flow_bmi),
    ("2", "BSA  — Body Surface Area (Mosteller)", flow_bsa),
    ("3", "BMR  — Basal Metabolic Rate (Mifflin-St Jeor)", flow_bmr),
    ("4", "IBW  — Ideal Body Weight (Devine)", flow_ibw),
    ("5", "CrCl — Creatinine Clearance (Cockcroft-Gault)", flow_crcl),
)


def print_menu():
    print(c.title("\n=== VitalScope — Clinical Health Metrics ==="))
    for key, label, _ in MENU:
        print(f"  {c.value(key)}. {label}")
    print(f"  {c.value('r')}. Save report to .txt")
    print(f"  {c.value('h')}. View saved history")
    print(f"  {c.value('q')}. Quit")


def export_report(session):
    """Write the current session history to a .txt report and report where."""
    if not session:
        print(c.warn("  Nothing to export yet — run a calculation first."))
        return
    try:
        path = report.save_report(session)
    except OSError as exc:
        print(c.error(f"  ! Could not save report: {exc}"))
        return
    print(c.good(f"  Report saved to: {path}"))


def view_history():
    """Show all persisted calculations from previous and current sessions."""
    records = history_store.load_history()
    if not records:
        print(c.warn("  No saved history yet."))
        return
    print(c.title(f"\n--- Saved history ({len(records)} entries) ---"))
    for i, entry in enumerate(records, start=1):
        stamp = entry.get("time", "?")
        print(f"  {i}. [{c.dim(stamp)}] {entry.get('summary', '')}")

    # Offer to clear the persisted history.
    if read_choice("\nClear all saved history? [y/n]: ",
                   {"y": "yes", "n": "no"}) == "yes":
        removed = history_store.clear_history()
        print(c.good("  History cleared.") if removed
              else c.warn("  Nothing to clear."))


def load_config():
    """Load reference ranges from config, applying them or warning on error."""
    try:
        ranges = config.load_reference_ranges()
        config.apply_reference_ranges(ranges)
    except config.ConfigError as exc:
        print(c.warn(f"  ! Config problem, using built-in defaults: {exc}"))
        return
    if ranges["source"] != "defaults":
        print(c.dim(f"  Reference ranges loaded from {ranges['source']}"))


def record_calculation(session, summary):
    """Store a result in the session list and append it to persistent history."""
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
    }
    session.append(entry)
    try:
        history_store.append_entry(entry)
    except OSError as exc:
        # Persistence is best-effort; never let it break the session.
        print(c.warn(f"  (could not save to history: {exc})"))


def main():
    print(c.title("VitalScope CLI") +
          c.dim(" — educational use only, not for clinical decisions."))
    load_config()
    unit = choose_units()
    session = []  # this run's results: list of {"time": str, "summary": str}

    # Build a quick lookup: menu key -> flow function.
    flows = {key: func for key, _, func in MENU}

    while True:
        print_menu()
        choice = input("Select an option: ").strip().lower()

        if choice in ("q", "quit", "exit"):
            break
        if choice == "r":  # export session report
            export_report(session)
            continue
        if choice == "h":  # view persisted history
            view_history()
            continue
        if choice == "u":  # hidden shortcut: switch units mid-session
            unit = choose_units()
            continue
        if choice not in flows:
            print(c.error("  ! Invalid option. Choose a number from the menu or 'q'."))
            continue

        try:
            summary = flows[choice](unit)
            record_calculation(session, summary)
        except KeyboardInterrupt:
            print(c.warn("\n  (cancelled)"))

    # Session summary on exit.
    if session:
        print(c.title("\n--- Session summary ---"))
        for entry in session:
            print(f"  - {entry['summary']}")
        # Offer to save a report before leaving.
        if read_choice("\nSave a .txt report? [y/n]: ",
                       {"y": "yes", "n": "no"}) == "yes":
            export_report(session)
    print(c.good("\nGoodbye. Stay healthy!"))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Goodbye!")
