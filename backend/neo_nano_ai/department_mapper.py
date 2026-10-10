"""Map Neo Nano diseases to the hospital's Departments.xlsx departments."""

import pandas as pd
from config import DEPARTMENT_FILE


# Body-system routing. Values must be names that exist in Departments.xlsx.
BODY_SYSTEM_TO_DEPARTMENT = {
    "cardiovascular": ["Cardiology"],
    "neurologic": ["Neurology"],
    "respiratory": ["Pulmonology"],
    "endocrine": ["General Medicine"],
    "gastrointestinal": ["Gastroenterology"],
    "renal": ["Nephrology"],
    "genitourinary": ["Urology"],
    "hematologic": ["General Medicine"],
    "oncologic": ["Oncology"],
    "musculoskeletal": ["Orthopedics"],
    "rheumatologic": ["General Medicine", "Orthopedics"],
    "dermatologic": ["Dermatology"],
    "ophthalmic": ["Ophthalmology"],
    "psychiatric": ["General Medicine"],
    "obstetric_gynecologic": ["Gynecology"],
    "obstetric": ["Gynecology"],
    "gynecologic": ["Gynecology"],
    "congenital_pediatric": ["Pediatrics"],
    "pediatric": ["Pediatrics"],
    "otolaryngologic": ["ENT"],
    "infectious": ["General Medicine"],
    "immune": ["General Medicine"],
    "genetic": ["General Medicine"],
    "multisystem": ["General Medicine"],
    "critical_care": ["General Medicine"],
    "rehabilitation": ["General Medicine"],
    "pain": ["General Medicine"],
    "toxicology": ["General Medicine"],
}

# Disease-name overrides for conditions that are commonly routed to a
# surgical service even when their broad body system is gastrointestinal,
# neurologic, etc. These are routing categories, not diagnoses.
DISEASE_NAME_OVERRIDES = {
    "General Surgery": [
        "appendicitis", "acute appendicitis", "cholecystitis",
        "gallstone", "gallstones", "cholelithiasis", "hernia",
        "bowel obstruction", "intestinal obstruction", "volvulus",
        "perforated", "perforation", "abscess", "fistula",
        "hemorrhoid", "pilonidal", "wound", "trauma", "laceration",
        "acute abdomen", "peritonitis", "necrotizing fasciitis",
        "pancreatic pseudocyst", "intestinal perforation",
    ],
    "Oncology": [
        "leukemia", "lymphoma", "myeloma", "sarcoma", "carcinoma",
        "malignant", "malignancy", "metastatic", "cancer", "tumor", "tumour",
    ],
    "Pediatrics": [
        "neonatal", "newborn", "infant", "childhood", "pediatric",
        "paediatric", "failure to thrive", "kawasaki",
    ],
}



# The 1667-row source intentionally has blank body_system fields. These name
# rules provide hospital routing without changing the disease source records.
DEPARTMENT_NAME_HINTS = {
    "Cardiology": ["heart", "cardiac", "coronary", "myocardial", "aortic", "atrial", "ventricular", "artery", "arrhythmia", "cardiomyopathy", "pericard", "hypertension"],
    "Neurology": ["brain", "neurolog", "neuro", "stroke", "seizure", "epilepsy", "migraine", "parkinson", "alzheimer", "multiple sclerosis", "dementia", "meningitis", "encephal", "neuropathy", "amyotrophic lateral sclerosis", "acoustic neuroma"],
    "Pulmonology": ["lung", "pulmonary", "respiratory", "pneumonia", "bronch", "asthma", "copd", "silicosis", "asbestosis", "sleep apnea"],
    "Gastroenterology": ["gastr", "stomach", "intestinal", "intestin", "bowel", "colon", "colitis", "crohn", "ulcerative colitis", "esoph", "hepatic", "hepatitis", "liver", "pancreat", "gallbladder", "biliary", "cirrhosis", "cholecyst", "achalasia"],
    "Nephrology": ["kidney", "renal", "nephri", "nephro", "glomerulo", "uremic", "proteinuria", "pyelonephritis"],
    "Urology": ["urinary", "ureter", "urethra", "bladder", "prostate", "prostatic", "testicular", "testis", "cystitis", "kidney stone", "renal stone"],
    "Ophthalmology": ["retinal", "retina", "optic", "ocular", "eye", "glaucoma", "cataract", "macular", "conjunctivitis", "amblyopia", "vision"],
    "ENT": ["ear", "otitis", "hearing", "sinus", "sinusitis", "nasal", "nose", "throat", "laryng", "tonsil", "pharyng", "otolaryng"],
    "Dermatology": ["skin", "dermat", "acne", "eczema", "psoriasis", "alopecia", "melanoma", "nevus", "urticaria", "vitiligo"],
    "Orthopedics": ["bone", "joint", "fracture", "arthritis", "musculoskeletal", "tendon", "ligament", "cartilage", "spine", "vertebr", "osteoporosis", "spondyl"],
    "Gynecology": ["ovarian", "ovary", "uterine", "uterus", "cervical", "cervix", "endometri", "adenomyosis", "fibroid", "vaginal", "vulvar", "gynecologic", "pregnancy", "pregnant", "obstetric", "breast"],
    "Pediatrics": ["pediatric", "paediatric", "childhood", "neonatal", "newborn", "infant", "congenital", "failure to thrive"],
    "Oncology": ["cancer", "carcinoma", "sarcoma", "leukemia", "lymphoma", "myeloma", "malignant", "malignancy", "metastatic", "tumor", "tumour", "neoplasm"],
}

def _name_hint_departments(name):
    text = str(name or "").casefold()
    found=[]
    for department, hints in DEPARTMENT_NAME_HINTS.items():
        if any(h.casefold() in text for h in hints):
            found.append(department)
    return found

def load_departments():
    try:
        df = pd.read_excel(DEPARTMENT_FILE, dtype=object).fillna("")
        df.columns = [str(c).strip() for c in df.columns]
        column = next((c for c in df.columns if c.casefold() == "department"), None)
        if column is None:
            return []
        return [str(v).strip() for v in df[column].tolist() if str(v).strip()]
    except Exception as exc:
        print(f"[WARNING] Could not load Departments.xlsx: {exc}")
        return []


HOSPITAL_DEPARTMENTS = load_departments()


def normalize_department(value):
    return " ".join(str(value or "").strip().casefold().split())


def canonical_department(value):
    target = normalize_department(value)
    for department in HOSPITAL_DEPARTMENTS:
        if normalize_department(department) == target:
            return department
    return None


def _name_override_departments(name):
    text = str(name or "").casefold()
    result = []
    for department, phrases in DISEASE_NAME_OVERRIDES.items():
        if any(phrase in text for phrase in phrases):
            result.append(department)
    return result


def departments_for(body_system, disease_name=""):
    """Return exact department names from Departments.xlsx."""
    candidates = _name_override_departments(disease_name)
    if not candidates:
        candidates = _name_hint_departments(disease_name)
    if not candidates:
        candidates = BODY_SYSTEM_TO_DEPARTMENT.get(
            str(body_system or "").strip().casefold(),
            ["General Medicine"],
        )

    valid = []
    for department in candidates:
        exact = canonical_department(department)
        if exact and exact not in valid:
            valid.append(exact)

    if not valid:
        fallback = canonical_department("General Medicine")
        return [fallback] if fallback else []
    return valid


def department_exists(department):
    return canonical_department(department) is not None
