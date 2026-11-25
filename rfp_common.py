"""Shared settings and helpers for the RFP automation scripts."""

import csv
import sys
from pathlib import Path

BASE_MODEL = "gpt-4o-mini-2024-07-18"

# Used both when building training data and when generating answers, so the
# fine-tuned model sees the same system prompt at inference that it saw in training.
ANSWER_SYSTEM_PROMPT = """You are a Census (www.getcensus.com) Solutions Engineer answering a prospective customer's RFP.
- Answer accurately and plainly, in 2-3 full sentences.
- Start by stating clearly whether Census supports the requirement.
- Keep a polite, professional tone.
- If you are not sure, say so and suggest confirming with the Census team rather than guessing."""

REFORMAT_SYSTEM_PROMPT = """Turn a prospective customer's RFP requirement into a single question about Census (www.getcensus.com).
Usually the question asks whether Census supports a feature or integration.
Example requirement: "Support Databricks as a source"
Example output: "Does Census support Databricks as a source integration?"
Return only the question."""


def read_csv(path):
    """Return (rows, fieldnames). utf-8-sig strips the BOM that Excel adds to CSV exports."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def choose_column(fieldnames, label, given=None):
    """Use the column named on the command line, or ask the user to pick one by number."""
    if given:
        if given not in fieldnames:
            sys.exit(f"Column '{given}' not found. Columns are: {', '.join(fieldnames)}")
        return given

    print(f"\nColumns in this file:")
    for i, name in enumerate(fieldnames):
        print(f"  {i}) {name}")
    choice = input(f"Number of the {label} column: ").strip()
    if not choice.isdigit() or int(choice) >= len(fieldnames):
        sys.exit("Invalid selection. Please retry.")
    column = fieldnames[int(choice)]
    print(f"{label.capitalize()} column: {column}")
    return column


def default_output_path(csv_path, suffix):
    p = Path(csv_path)
    return str(p.with_name(f"{p.stem}_{suffix}{p.suffix}"))
