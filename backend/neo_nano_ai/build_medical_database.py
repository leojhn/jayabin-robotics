
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "medical" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "medical" / "processed"

REQUIRED_FIELDS = {
    "id", "entity_type", "name", "aliases", "description", "symptoms",
    "body_system", "related_entities", "knowledge_graph",
    "clinical_rules", "genomics_data", "source", "status", "version"
}

def normalize(value):
    return " ".join(str(value).casefold().split())

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    seen_ids = {}
    seen_names = {}
    duplicates = []
    invalid = []
    files = sorted(RAW_DIR.glob("*.jsonl"))

    for path in files:
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    invalid.append({"file": path.name, "line": line_no, "error": str(exc)})
                    continue

                missing = sorted(REQUIRED_FIELDS - set(record))
                if missing:
                    invalid.append({
                        "file": path.name, "line": line_no,
                        "id": record.get("id"), "error": "missing_fields",
                        "fields": missing
                    })
                    continue

                record_id = normalize(record["id"])
                record_name = normalize(record["name"])

                if record_id in seen_ids:
                    duplicates.append({
                        "type": "id", "value": record["id"],
                        "kept_from": seen_ids[record_id], "duplicate_from": path.name
                    })
                    continue

                if record_name in seen_names:
                    duplicates.append({
                        "type": "name", "value": record["name"],
                        "kept_from": seen_names[record_name], "duplicate_from": path.name
                    })
                    continue

                seen_ids[record_id] = path.name
                seen_names[record_name] = path.name
                records.append(record)

    records.sort(key=lambda x: x["id"])

    master_jsonl = PROCESSED_DIR / "diseases_master.jsonl"
    master_json = PROCESSED_DIR / "diseases_master.json"
    lookup_json = PROCESSED_DIR / "disease_lookup.json"
    report_json = PROCESSED_DIR / "validation_report.json"

    with master_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    master_json.write_text(json.dumps({
        "dataset_name": "Neo Nano Medical Knowledge Base",
        "record_count": len(records),
        "records": records
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lookup = {}
    for record in records:
        terms = [record.get("name", "")] + record.get("aliases", [])
        for term in terms:
            term = normalize(term)
            if term:
                lookup.setdefault(term, []).append(record["id"])

    lookup_json.write_text(json.dumps(lookup, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "source_files": [p.name for p in files],
        "valid_records": len(records),
        "duplicate_records_skipped": len(duplicates),
        "invalid_records_skipped": len(invalid),
        "duplicates": duplicates,
        "invalid_records": invalid,
        "status": "ready" if records else "waiting_for_dataset_files"
    }
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
