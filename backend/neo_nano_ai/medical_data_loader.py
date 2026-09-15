
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "medical" / "processed"
MASTER_JSONL = PROCESSED_DIR / "diseases_master.jsonl"

_CACHE = None

def load_master_records():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not MASTER_JSONL.exists():
        return []
    records = []
    with MASTER_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    _CACHE = records
    return _CACHE

def normalize(text):
    return " ".join(str(text).lower().split())

def build_lookup(records):
    lookup = {}
    for record in records:
        for value in [record.get("name", "")] + record.get("aliases", []):
            value = normalize(value)
            if value:
                lookup.setdefault(value, []).append(record["id"])
    return lookup
