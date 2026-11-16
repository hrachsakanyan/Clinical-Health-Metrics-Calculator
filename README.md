# 🩺 VitalScope 

### Clinical Health Metrics Calculator

A clean, menu-driven **command-line tool** that computes five core clinical
health metrics from basic body measurements — with input validation,
severity-based categories, and short interpretations.

> [!WARNING]
> **Educational project only.** VitalScope is **not a medical device** and must
> **not** be used for diagnosis, treatment, or any clinical decision-making.
> Always consult a qualified healthcare professional.

---

## 📚 Table of Contents

* [✨ Features](#-features)
* [🧬 Medical Formulas](#-medical-formulas)
* [📦 Installation](#-installation)
* [🚀 Usage](#-usage)
* [⚙️ Configuration](#️-configuration)
* [🗂️ Project Structure](#-project-structure)
* [🧪 Running the Tests](#-running-the-tests)
* [📄 License](#-license)

---

## ✨ Features

|     | Feature                                                                  |
| --- | ------------------------------------------------------------------------ |
| 🎛️ | **Menu-based CLI** — pick the calculation you want                       |
| 🧮  | **Five calculators** in one program (BMI, BSA, BMR, IBW, CrCl)           |
| 🛡️ | **Robust input validation** — numbers, ranges, and choices are checked   |
| 🏷️ | **Categorized output** with a short interpretation                       |
| 📐  | **Metric & Imperial units** — switch any time with `u`                   |
| 🌈  | **Colored output** — green = normal, yellow = borderline, red = abnormal |
| 📋  | **Session summary** printed on exit                                      |
| 💾  | **Export a** **`.txt`** **report** — timestamped, saved to `reports/`    |
| ⚙️  | **Configurable reference ranges** via a simple JSON file                 |
| 🗃️ | **Persistent history** — calculations survive across runs (JSONL)        |

> 🌈 Colors use [`colorama`](https://pypi.org/project/colorama/) when installed
> and **fall back to plain text automatically** when it isn't — so the tool has
> **zero required dependencies**.

---

## 🧬 Medical Formulas

| Metric                          | Formula                                       | Reference                              |
| ------------------------------- | --------------------------------------------- | -------------------------------------- |
| **BMI** — Body Mass Index       | `weight(kg) / height(m)²`                     | WHO BMI classification                 |
| **BSA** — Body Surface Area     | `√((height_cm × weight_kg) / 3600)`           | Mosteller RD, *N Engl J Med* 1987      |
| **BMR** — Basal Metabolic Rate  | `10·kg + 6.25·cm − 5·age (+5 ♂ / −161 ♀)`     | Mifflin–St Jeor, *Am J Clin Nutr* 1990 |
| **IBW** — Ideal Body Weight     | `50 / 45.5 kg + 2.3 kg per inch over 60 in`   | Devine BJ, 1974                        |
| **CrCl** — Creatinine Clearance | `((140 − age) × kg × sexFactor) / (72 × SCr)` | Cockcroft–Gault, *Nephron* 1976        |

`sexFactor = 1.0` (male) or `0.85` (female). Serum creatinine (`SCr`) in mg/dL.

---

## 📦 Installation

Requires **Python 3.8+**. The tool runs on the standard library alone;
`colorama` is an **optional** extra that enables colored output.

```bash
git clone https://github.com/<your-username>/vitalscope.git
cd vitalscope
pip install -r requirements.txt   # optional: installs colorama for colors
```

---

## 🚀 Usage 

```bash
python src/main.py
```

```text
VitalScope CLI — educational use only, not for clinical decisions.
Units [m = metric, i = imperial]: m

=== VitalScope — Clinical Health Metrics ===
  1. BMI  — Body Mass Index
  2. BSA  — Body Surface Area (Mosteller)
  3. BMR  — Basal Metabolic Rate (Mifflin-St Jeor)
  4. IBW  — Ideal Body Weight (Devine)
  5. CrCl — Creatinine Clearance (Cockcroft-Gault)
  r. Save report to .txt
  h. View saved history
  q. Quit
Select an option: 1
Weight (kg): 70
Height (cm): 175

  BMI: 22.9 kg/m^2
  Category: Normal weight
```

**Menu shortcuts:** `r` export report · `h` view history · `u` switch units · `q` quit

---

## ⚙️ Configuration 

Reference ranges live in
`config/reference_ranges.json`.
Each entry is a `[bound, label]` pair:

* **BMI** — `bound` is the *exclusive upper limit* of the category. Use the
  string `"inf"` for the open-ended top category.
* **CrCl** — `bound` is the *inclusive lower limit* of the stage.

```json
{
  "bmi_categories": [
    [18.5, "Underweight"],
    [25.0, "Normal weight"],
    ["inf", "Above normal"]
  ],
  "crcl_stages": [
    [90.0, "Normal"],
    [0.0, "Reduced"]
  ]
}
```

If the file is missing or malformed, VitalScope prints a note and falls back
to built-in defaults — it never fails to start.

---

## 🗂️ Project Structure

```text
vitalscope/
├── src/
│   ├── main.py          # CLI: menu, input handling, output
│   ├── calculators.py   # Pure formula functions + lookup tables
│   ├── colors.py        # Optional colorama color layer (graceful fallback)
│   ├── report.py        # Build & save timestamped .txt session reports
│   ├── config.py        # Load reference ranges from JSON
│   └── history.py       # Persist session results across runs (JSONL)
├── config/
│   └── reference_ranges.json
├── tests/               # 33 unit tests
│   ├── test_calculators.py
│   ├── test_report.py
│   ├── test_config.py
│   └── test_history.py
├── README.md
├── requirements.txt
└── .gitignore
```

**Design note:** the math (`calculators.py`) is kept **pure and separate** from
the display, config, and persistence layers — so every formula is trivial to
test and reuse.

---

## 🧪 Running the Tests

```bash
python -m unittest discover -s tests
```

Or, if you prefer `pytest`:

```bash
pip install pytest
pytest tests/
```

Expected result: **`Ran 33 tests ... OK`** ✅

---

## 📄 License

Released under the **MIT License** for educational purposes.
See the disclaimer at the top of this file.
