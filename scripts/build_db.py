#!/usr/bin/env python3
"""Compile systems/*.yaml into machine-readable database formats.

Outputs:
  data/systems.json  - full dataset as a JSON array (the canonical API)
  data/index.json    - lookup indexes: system ids grouped by strategy,
                       principle, technology, technique, developer, status
  data/systems.db    - SQLite database (systems + join tables), for SQL
                       queries and tools like datasette

Usage: python scripts/build_db.py
"""
import json
import sqlite3
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

systems = []
for path in sorted((ROOT / "systems").glob("*.yaml")):
    doc = yaml.safe_load(path.read_text())
    doc["id"] = path.stem
    systems.append(doc)

# ---- JSON dataset ----
(DATA / "systems.json").write_text(
    json.dumps(systems, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
)

# ---- Indexes ----
index = {"by_strategy": {}, "by_principle": {}, "by_technology": {},
         "by_technique": {}, "by_developer": {}, "by_status": {}}
for s in systems:
    sid = s["id"]
    for h in s.get("hoepman") or []:
        index["by_strategy"].setdefault(h["strategy"], []).append(sid)
    for o in s.get("oecd") or []:
        index["by_principle"].setdefault(o["principle"], []).append(sid)
    for t in s.get("technologies") or []:
        index["by_technology"].setdefault(t, []).append(sid)
    for t in s.get("techniques") or []:
        index["by_technique"].setdefault(t, []).append(sid)
    if s.get("developer"):
        index["by_developer"].setdefault(s["developer"], []).append(sid)
    index["by_status"].setdefault(s.get("status", "unknown"), []).append(sid)
for k in index:
    index[k] = dict(sorted(index[k].items()))
(DATA / "index.json").write_text(
    json.dumps(index, indent=1, ensure_ascii=False) + "\n"
)

# ---- SQLite ----
db_path = DATA / "systems.db"
db_path.unlink(missing_ok=True)
con = sqlite3.connect(db_path)
con.executescript("""
CREATE TABLE systems (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, developer TEXT, status TEXT,
  analysis_status TEXT, date TEXT, source TEXT, description TEXT, notes TEXT
);
CREATE TABLE hoepman (
  system_id TEXT REFERENCES systems(id), strategy TEXT, rationale TEXT
);
CREATE TABLE oecd (
  system_id TEXT REFERENCES systems(id), principle TEXT, rationale TEXT
);
CREATE TABLE technologies (
  system_id TEXT REFERENCES systems(id), technology TEXT
);
CREATE TABLE techniques (
  system_id TEXT REFERENCES systems(id), technique TEXT
);
CREATE INDEX idx_hoepman ON hoepman(strategy);
CREATE INDEX idx_oecd ON oecd(principle);
CREATE INDEX idx_tech ON technologies(technology);
CREATE INDEX idx_techq ON techniques(technique);
""")
for s in systems:
    con.execute(
        "INSERT INTO systems VALUES (?,?,?,?,?,?,?,?,?)",
        (s["id"], s["name"], s.get("developer"), s.get("status"),
         s.get("analysis_status"), s.get("date"), s.get("source"),
         s.get("description"), s.get("notes")),
    )
    for h in s.get("hoepman") or []:
        con.execute("INSERT INTO hoepman VALUES (?,?,?)",
                    (s["id"], h["strategy"], h["rationale"]))
    for o in s.get("oecd") or []:
        con.execute("INSERT INTO oecd VALUES (?,?,?)",
                    (s["id"], o["principle"], o["rationale"]))
    for t in s.get("technologies") or []:
        con.execute("INSERT INTO technologies VALUES (?,?)", (s["id"], t))
    for t in s.get("techniques") or []:
        con.execute("INSERT INTO techniques VALUES (?,?)", (s["id"], t))
con.commit()
con.close()

print(f"Built data/systems.json, data/index.json, data/systems.db "
      f"({len(systems)} systems)")
