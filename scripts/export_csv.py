#!/usr/bin/env python3
"""Export all system YAML files to a single CSV (for Google Sheets import).

Usage: python scripts/export_csv.py > s3d-taxonomy.csv
"""
import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

writer = csv.writer(sys.stdout)
writer.writerow([
    "Developed by", "Name of system", "Status", "Analysis status", "Date",
    "Link to source", "Description", "Hoepman strategies (with rationale)",
    "OECD principles (with rationale)", "Technologies", "Techniques", "Notes",
])

for path in sorted((ROOT / "systems").glob("*.yaml")):
    d = yaml.safe_load(path.read_text())
    hoep = "\n".join(f"{h['strategy']}: {h['rationale']}" for h in d.get("hoepman", []))
    oecd = "\n".join(f"{o['principle']}: {o['rationale']}" for o in d.get("oecd", []))
    writer.writerow([
        d.get("developer") or "", d["name"], d.get("status") or "",
        d.get("analysis_status") or "", d.get("date") or "", d.get("source") or "",
        d.get("description") or "", hoep, oecd,
        ", ".join(d.get("technologies", [])), ", ".join(d.get("techniques", [])),
        d.get("notes") or "",
    ])
