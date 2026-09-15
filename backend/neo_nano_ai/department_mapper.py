
BODY_SYSTEM_TO_DEPARTMENT = {
    "cardiovascular": ["Cardiology"],
    "neurologic": ["Neurology"],
    "respiratory": ["Pulmonology"],
    "endocrine": ["General Medicine", "Endocrinology"],
    "gastrointestinal": ["Gastroenterology", "General Medicine"],
    "renal": ["Nephrology"],
    "genitourinary": ["Urology"],
    "hematologic": ["General Medicine", "Oncology"],
    "oncologic": ["Oncology"],
    "musculoskeletal": ["Orthopedics"],
    "rheumatologic": ["General Medicine", "Orthopedics"],
    "dermatologic": ["Dermatology"],
    "ophthalmic": ["Ophthalmology"],
    "psychiatric": ["General Medicine"],
    "obstetric_gynecologic": ["Gynecology"],
    "congenital_pediatric": ["Pediatrics"],
    "infectious": ["General Medicine"],
    "multisystem": ["General Medicine"]
}

def departments_for(body_system):
    return BODY_SYSTEM_TO_DEPARTMENT.get(body_system, ["General Medicine"])
