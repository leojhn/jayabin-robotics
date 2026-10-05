import re
from collections import defaultdict

from .medical_data_loader import load_master_records, normalize
from .department_mapper import departments_for, canonical_department, HOSPITAL_DEPARTMENTS


# ============================================================
# EMERGENCY TERMS
# ============================================================

EMERGENCY_TERMS = {
    "chest pain",
    "severe breathing difficulty",
    "difficulty breathing",
    "unconscious",
    "loss of consciousness",
    "stroke",
    "severe bleeding",
    "seizure",
    "suicidal",
}


# ============================================================
# DIRECT DEPARTMENT INTENT
#
# These are routing hints for the hospital demo.
# They do NOT diagnose a disease.
#
# The hospital's General Enquiries data explicitly maps:
#   kidney diseases -> Nephrology
#   urinary problems -> Urology
# ============================================================

DEPARTMENT_INTENT_RULES = [
    (
        "Nephrology",
        [
            "kidney disease",
            "kidney diseases",
            "kidney problem",
            "kidney problems",
            "kidney failure",
            "renal disease",
            "renal diseases",
            "renal failure",
            "chronic kidney disease",
            "ckd",
            "nephritis",
            "glomerulonephritis",
            "protein in urine",
            "high creatinine",
            "creatinine is high",
        ],
    ),
    (
        "Urology",
        [
            "kidney stone",
            "kidney stones",
            "renal stone",
            "renal stones",
            "urinary problem",
            "urinary problems",
            "urinary difficulty",
            "difficulty urinating",
            "pain while urinating",
            "painful urination",
            "burning urination",
            "blood in urine",
            "blood while urinating",
            "bladder problem",
            "bladder problems",
            "prostate problem",
            "prostate problems",
            "urine problem",
            "urine problems",
        ],
    ),
    (
        "Cardiology",
        [
            "heart problem",
            "heart problems",
            "heart disease",
            "heart diseases",
            "cardiac problem",
            "cardiac problems",
            "palpitations",
        ],
    ),
    (
        "Pulmonology",
        [
            "lung problem",
            "lung problems",
            "lung disease",
            "lung diseases",
            "breathing problem",
            "breathing problems",
            "respiratory problem",
            "respiratory problems",
        ],
    ),
    (
        "Neurology",
        [
            "brain problem",
            "brain problems",
            "neurological problem",
            "neurological problems",
            "nerve problem",
            "nerve problems",
            "migraine",
        ],
    ),
    (
        "Gastroenterology",
        [
            "stomach problem",
            "stomach problems",
            "digestive problem",
            "digestive problems",
            "intestinal problem",
            "intestinal problems",
        ],
    ),
    (
        "General Medicine",
        [
            "hormonal disorder",
            "hormonal disorders",
            "hormone problem",
            "hormone problems",
            "thyroid problem",
            "thyroid problems",
        ],
    ),
    (
        "Oncology",
        [
            "cancer",
            "cancer problem",
            "cancer problems",
            "tumor",
            "tumour",
        ],
    ),
    (
        "Gynecology",
        [
            "pregnancy",
            "pregnant",
            "pregnancy problem",
            "pregnancy problems",
        ],
    ),
]


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", normalize(text)))


def _department_intent(query):
    """
    Return explicit department-routing evidence from the patient's
    wording.

    The return value is:
        [(department, score, matched_phrases), ...]
    """
    q = normalize(query)
    matches = []

    for department, phrases in DEPARTMENT_INTENT_RULES:
        matched = []

        for phrase in phrases:
            phrase_normalized = normalize(phrase)

            if phrase_normalized and phrase_normalized in q:
                matched.append(phrase)

        if matched:
            # Longer / more specific phrases get slightly more weight.
            score = 100.0 + max(len(p.split()) for p in matched)
            matches.append(
                (
                    department,
                    score,
                    matched,
                )
            )

    matches.sort(key=lambda item: item[1], reverse=True)
    return matches


def retrieve(query, limit=5, department=None):
    records = load_master_records()
    q = normalize(query)

    # When a department is supplied, restrict disease retrieval to diseases
    # that map to that exact hospital department. This keeps the retriever
    # aligned with Departments.xlsx rather than using free-text department
    # names from the medical dataset.
    selected_department = canonical_department(department) if department else None
    if department and not selected_department:
        raise ValueError(
            f"Unknown department '{department}'. Valid departments: "
            + ", ".join(HOSPITAL_DEPARTMENTS)
        )
    qt = _tokens(q)
    results = []

    for record in records:
        record_departments = departments_for(record.get("body_system"), record.get("name", ""))

        if selected_department and selected_department not in record_departments:
            continue

        score = 0.0
        matched = []

        name = normalize(record.get("name", ""))
        aliases = [
            normalize(a)
            for a in record.get("aliases", [])
        ]
        symptoms = [
            normalize(s)
            for s in record.get("symptoms", [])
        ]

        # --------------------------------------------------------
        # Disease-name match
        # --------------------------------------------------------

        if name and name in q:
            score += 12
            matched.append(record.get("name"))

        # --------------------------------------------------------
        # Alias match
        # --------------------------------------------------------

        for alias in aliases:
            if alias and alias in q:
                score += 9
                matched.append(alias)

        # --------------------------------------------------------
        # Symptom match
        # --------------------------------------------------------

        for symptom in symptoms:
            st = _tokens(symptom)

            if not st:
                continue

            if symptom in q:
                score += 6 + min(len(st), 3)
                matched.append(symptom)

            else:
                overlap = len(qt & st)

                # Avoid scoring generic one-word overlaps such as
                # "pain" equally for every disease.
                if overlap:
                    coverage = overlap / len(st)

                    if len(st) == 1:
                        score += 1.5

                    elif coverage >= 0.5:
                        score += overlap * 2.0
                        matched.append(symptom)

                    elif overlap >= 2:
                        score += overlap * 1.0
                        matched.append(symptom)

        if score > 0:
            results.append(
                {
                    "id": record["id"],
                    "name": record["name"],
                    "description": record.get("description"),
                    "body_system": record.get("body_system"),
                    "matched_features": list(
                        dict.fromkeys(matched)
                    )[:8],
                    "score": round(score, 2),
                    "recommended_departments": record_departments,
                    "department": record_departments[0] if record_departments else None,
                }
            )

    results.sort(
        key=lambda x: (
            x["score"],
            len(x["matched_features"]),
        ),
        reverse=True,
    )

    return results[:limit]


def triage(query):
    text = normalize(query)

    matched = [
        term
        for term in EMERGENCY_TERMS
        if term in text
    ]

    if matched:
        return {
            "urgency": "high",
            "message": (
                "The information provided may require "
                "urgent clinical assessment."
            ),
            "matched_alert_terms": matched,
        }

    return {
        "urgency": "routine",
        "message": (
            "This result is informational and does not "
            "establish a diagnosis."
        ),
        "matched_alert_terms": [],
    }


def analyze(query, limit=5, department=None):
    """
    Analyze a Neo Nano query.

    The disease/knowledge-base retrieval is preserved.
    Department routing is then calculated from:

    1. Explicit department intent in the patient's wording.
    2. Department evidence attached to retrieved records.

    Explicit wording gets priority so a query such as
    "I have a kidney problem" does not fall back to
    General Medicine simply because a generic disease match
    happened to score higher.
    """

    query = str(query or "").strip()

    selected_department = canonical_department(department) if department else None
    if department and not selected_department:
        raise ValueError(
            f"Unknown department '{department}'. Valid departments: "
            + ", ".join(HOSPITAL_DEPARTMENTS)
        )

    matches = retrieve(query, limit, selected_department)

    # --------------------------------------------------------
    # Department evidence from retrieved knowledge records
    # --------------------------------------------------------

    department_scores = defaultdict(float)

    for match in matches:
        for department in match.get(
            "recommended_departments",
            [],
        ):
            department_scores[department] += float(
                match.get("score", 0)
            )

    # --------------------------------------------------------
    # Explicit department intent
    # --------------------------------------------------------

    intent_matches = _department_intent(query)

    intent_departments = []

    for intent_department, score, matched_phrases in intent_matches:
        if selected_department and intent_department != selected_department:
            continue
        department_scores[intent_department] += score
        intent_departments.append(
            {
                "department": intent_department,
                "score": score,
                "matched_phrases": matched_phrases,
            }
        )

    # --------------------------------------------------------
    # Rank departments
    #
    # Explicit intent is represented by the large score above.
    # Therefore:
    #
    #   "kidney problem" -> Nephrology
    #   "kidney stone"   -> Urology
    #   "urinary problem" -> Urology
    #
    # without removing the knowledge-base evidence.
    # --------------------------------------------------------

    ranked = [
        department
        for department, _ in sorted(
            department_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    if selected_department:
        ranked = [selected_department]
    elif not ranked:
        ranked = ["General Medicine"]

    return {
        "query": query,
        "knowledge_base_records": len(
            load_master_records()
        ),
        "triage": triage(query),
        "possible_conditions": matches,
        "selected_department": selected_department,
        "available_departments": HOSPITAL_DEPARTMENTS,
        "recommended_departments": ranked[:3],
        "department_scores": dict(
            sorted(
                department_scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:5]
        ),
        "department_intent": intent_departments,
        "clinical_note": (
            "Possible matches are generated from the Neo Nano "
            "knowledge base and require qualified clinical "
            "assessment."
        ),
    }
