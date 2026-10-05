from flask import Blueprint, request, jsonify
import json
import os
import pandas as pd

neo = Blueprint("neo", __name__)

# -------------------------------------------------------
# Paths
# -------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(__file__))

DISEASE_FILE = os.path.join(
    BASE,
    "data",
    "medical",
    "processed",
    "diseases_master.jsonl"
)

TEST_FILE = os.path.join(
    BASE,
    "data",
    "medical",
    "processed",
    "medical_tests_master.jsonl"
)

DOCTOR_FILE = os.path.join(
    BASE,
    "excel",
    "Doctors.xlsx"
)

DEPARTMENT_FILE = os.path.join(
    BASE,
    "excel",
    "Departments.xlsx"
)

# -------------------------------------------------------
# Load data once
# -------------------------------------------------------

diseases = []
tests = []

if os.path.exists(DISEASE_FILE):
    with open(DISEASE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            diseases.append(json.loads(line))

if os.path.exists(TEST_FILE):
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            tests.append(json.loads(line))

doctors_df = pd.read_excel(DOCTOR_FILE).fillna("")
dept_df = pd.read_excel(DEPARTMENT_FILE).fillna("")

print(f"Loaded Diseases : {len(diseases)}")
print(f"Loaded Doctors  : {len(doctors_df)}")
print(f"Loaded Tests    : {len(tests)}")


# -------------------------------------------------------
# Search disease
# -------------------------------------------------------

def search_department(symptoms):

    words = symptoms.lower().split()

    best = None
    score = 0

    for d in diseases:

        s = 0

        for keyword in d.get("keywords", []):

            if keyword.lower() in symptoms.lower():
                s += 2

        for w in words:
            if w in d.get("symptoms", "").lower():
                s += 1

        if s > score:
            score = s
            best = d

    return best, score


# -------------------------------------------------------
# Doctor list
# -------------------------------------------------------

def get_doctors(department):

    result = []

    for _, row in doctors_df.iterrows():

        dept = str(row.get("Department", "")).lower()

        if department.lower() == dept:

            result.append({
                "name": row.get("Doctor Name", ""),
                "specialization": row.get("Department", ""),
                "experience": row.get("Experience", "")
            })

    return result[:5]


# -------------------------------------------------------
# Medical tests
# -------------------------------------------------------

def get_tests(department):

    result = []

    for t in tests:

        dept = str(t.get("department", "")).lower()

        if dept == department.lower():

            result.append({
                "name": t.get("test_name", ""),
                "purpose": t.get("purpose", ""),
                "priority": t.get("priority", "Medium")
            })

    return result[:10]


# -------------------------------------------------------
# API
# -------------------------------------------------------

@neo.route("/api/neo_nano/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    symptoms = data.get("symptoms", "").strip()

    if symptoms == "":
        return jsonify({
            "error": "No symptoms provided."
        }), 400

    disease, score = search_department(symptoms)

    if disease is None:

        department = "General Medicine"

        conditions = ["General Consultation"]

        reason = "Symptoms require general medical evaluation."

    else:

        department = disease.get("department", "General Medicine")

        conditions = disease.get("possible_conditions", [])

        reason = disease.get("reason", "")

    doctors = get_doctors(department)

    medical_tests = get_tests(department)

    confidence = min(70 + score * 5, 99)

    return jsonify({

        "department": department,

        "confidence": confidence,

        "reason": reason,

        "conditions": conditions,

        "doctors": doctors,

        "tests": medical_tests

    })
