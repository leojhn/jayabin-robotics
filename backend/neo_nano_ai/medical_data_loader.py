import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "medical" / "processed"

# Primary Neo Nano source: the user's 1667-row diseases_master JSONL converted
# faithfully to diseases_master.json. The old 1186-record dataset is not used.
MASTER_JSON = PROCESSED_DIR / "diseases_master.json"
MASTER_JSONL = PROCESSED_DIR / "diseases_master.jsonl"
MASTER_JSONL_FALLBACK = PROCESSED_DIR / "diseases_master1.jsonl"
EXPECTED_RECORD_COUNT = 1667

_CACHE = None

def load_master_records():
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    records = []

    if MASTER_JSON.exists():
        try:
            payload = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
            records = payload.get("records", []) if isinstance(payload, dict) else payload
        except Exception as exc:
            print(f"[WARNING] Failed to load {MASTER_JSON.name}: {exc}")

    if not records:
        for path in (MASTER_JSONL, MASTER_JSONL_FALLBACK):
            if not path.exists():
                continue
            try:
                with path.open(encoding="utf-8") as f:
                    records = [json.loads(line) for line in f if line.strip()]
                if records:
                    break
            except Exception as exc:
                print(f"[WARNING] Failed to load {path.name}: {exc}")

    # Hard validation: never silently fall back to the old 1186-record dataset.
    if len(records) != EXPECTED_RECORD_COUNT:
        raise RuntimeError(
            f"Neo Nano disease source must contain exactly 1667 records; loaded {len(records)}."
        )

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
