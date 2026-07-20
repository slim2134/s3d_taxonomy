#!/usr/bin/env python3
"""Validate every YAML file in systems/ against schema/system.schema.json.

Usage: python scripts/validate.py
Exit code 0 = all valid, 1 = errors found.
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schema" / "system.schema.json").read_text())
validator = Draft7Validator(SCHEMA)

errors = 0
files = sorted((ROOT / "systems").glob("*.yaml"))
if not files:
    print("No system files found.")
    sys.exit(1)

for path in files:
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        print(f"FAIL {path.name}: YAML parse error: {e}")
        errors += 1
        continue

    file_errors = []
    for err in validator.iter_errors(doc):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        file_errors.append(f"  {loc}: {err.message}")

    # Semantic rule: complete entries need at least one strategy AND one principle
    if isinstance(doc, dict) and doc.get("analysis_status") == "complete":
        if not doc.get("hoepman"):
            file_errors.append("  analysis_status is 'complete' but hoepman is empty")
        if not doc.get("oecd"):
            file_errors.append("  analysis_status is 'complete' but oecd is empty")

    if file_errors:
        print(f"FAIL {path.name}")
        print("\n".join(file_errors))
        errors += 1

if errors:
    print(f"\n{errors}/{len(files)} files failed validation.")
    sys.exit(1)
print(f"All {len(files)} system files valid.")
