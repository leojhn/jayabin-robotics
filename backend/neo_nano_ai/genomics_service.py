
from .medical_data_loader import load_master_records

def get_genomics(disease_id):
    for record in load_master_records():
        if record.get("id") == disease_id:
            return {
                "id": disease_id,
                "name": record.get("name"),
                "genomics_data": record.get("genomics_data", {}),
                "note": "Genomics output is informational metadata. Patient-specific genomic interpretation must use validated clinical and laboratory data."
            }
    return None
