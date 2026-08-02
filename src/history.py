"""
history.py — Persist session results across runs.

Each calculation is appended as one JSON object per line (JSONL) to
data/history.jsonl. JSONL is append-friendly and resilient: one corrupt
line never breaks the rest of the file.

A record is a dict:
    {"time": "2026-08-02 14:33:05", "summary": "BMI: 22.9 kg/m^2 (Normal weight)"}
"""

import json
import os

# Default location: <project_root>/data/history.jsonl
DEFAULT_HISTORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "history.jsonl",
)


def append_entry(entry, path=None):
    """Append a single history record as one JSON line. Creates data/ if needed."""
    target = path or DEFAULT_HISTORY_PATH
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_history(path=None):
    """
    Return all persisted records as a list of dicts.

    Missing file -> empty list. Blank or malformed lines are skipped so a
    partially corrupt file still loads whatever is valid.
    """
    target = path or DEFAULT_HISTORY_PATH
    if not os.path.exists(target):
        return []

    records = []
    with open(target, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip a corrupt line, keep the rest
    return records


def clear_history(path=None):
    """
    Delete the persisted history file. Returns True if a file was removed,
    False if there was nothing to remove.
    """
    target = path or DEFAULT_HISTORY_PATH
    if os.path.exists(target):
        os.remove(target)
        return True
    return False
