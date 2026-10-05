from flask import Flask, jsonify, request, send_from_directory
import os
from flask_cors import CORS
from datetime import date, datetime
from numbers import Integral, Real

from patient_manager import PatientManager
from appointment_manager import AppointmentManager
from billing_manager import BillingManager
from map_manager import MapManager
from faq_manager import FAQManager
from printer import printer

from neo_nano_ai.disease_retriever import analyze, retrieve
from neo_nano_ai.knowledge_graph_service import build_global_graph
from neo_nano_ai.genomics_service import get_genomics
from neo_nano import neo
from voice.face_service import (
    identify as identify_face, enroll as enroll_face,
    start_camera, camera_status, latest_frame, enroll_from_camera
)

app = Flask(__name__)
CORS(app)

app.register_blueprint(neo)

bm = BillingManager()
am = AppointmentManager()
mm = MapManager()
fm = FAQManager()
pm = PatientManager()

import pandas as pd
import json

doctors_df = pd.read_excel("../excel/Doctors.xlsx").fillna("")

medical_tests = []

with open("../data/medical/processed/medical_tests_master.jsonl","r",encoding="utf-8") as f:
    for line in f:
        medical_tests.append(json.loads(line))


def make_json_safe(value):
    """Convert pandas/NumPy values to normal JSON-safe Python values."""

    if value is None:
        return None

    # Dictionaries and lists/tuples.
    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]

    # NumPy/Pandas integer values such as numpy.int64.
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)

    # NumPy/Pandas floating values such as numpy.float64.
    if isinstance(value, Real) and not isinstance(value, bool):
        return float(value)

    # NumPy/Pandas boolean values.
    if isinstance(value, bool):
        return bool(value)

    # Dates and timestamps.
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    # Pandas/NumPy missing values expose tolist/item in some cases.
    try:
        if value.__class__.__module__.startswith(("numpy", "pandas")):
            if hasattr(value, "item"):
                return make_json_safe(value.item())
    except Exception:
        pass

    return value

###########################################################

@app.route("/")
def home():
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend")
    )
    return send_from_directory(frontend_dir, "index.html")

###########################################################
# GET ALL PATIENTS
###########################################################

@app.route("/api/patients", methods=["GET"])
def get_patients():
    return jsonify(
        pm.get_all_patients()
    )

###########################################################
# GET PATIENT BY ID
###########################################################

@app.route("/api/patient/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = pm.get_patient_by_id(patient_id)
    if patient:
        return jsonify(patient)

    return jsonify({
        "success": False,
        "message": "Patient not found"
    })

###########################################################
# REGISTER PATIENT
###########################################################

@app.route("/api/register_patient", methods=["POST"])
def register_patient():
    data = request.get_json()
    patient_id = pm.register_patient(data)

    return jsonify({
        "success": True,
        "patient_id": patient_id
    })

###########################################################
# UPDATE PATIENT
###########################################################

@app.route("/api/update_patient/<patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.get_json()
    success = pm.update_patient(patient_id, data)

    return jsonify({
        "success": success
    })

###########################################################
# DELETE PATIENT
###########################################################

@app.route("/api/delete_patient/<patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    success = pm.delete_patient(patient_id)

    return jsonify({
        "success": success
    })

###########################################################
# AUTHENTICATION
###########################################################

@app.route("/api/authenticate", methods=["POST"])
def authenticate():
    data = request.get_json()
    patient_id = data.get("patient_id", "PAT-001")
    patient = pm.get_patient_by_id(patient_id)

    if patient:
        return jsonify({
            "success": True,
            "existing": True,
            "patient": patient
        })

    return jsonify({
        "success": True,
        "existing": False
    })

###########################################################
# BOOK APPOINTMENT
###########################################################

@app.route(
    "/api/book_appointment",
    methods=["POST"]
)
def book_appointment():
    try:
        data = request.get_json(silent=True) or {}
        required_fields = [
            "patient_id",
            "department",
            "doctor",
            "date",
            "time"
        ]

        missing = [
            field for field in required_fields
            if not str(data.get(field, "")).strip()
        ]

        if missing:
            return jsonify({
                "success": False,
                "message":
                    "Missing appointment data: " +
                    ", ".join(missing)
            }), 400

        result = am.book_appointment(
            patient_id=str(data["patient_id"]).strip(),
            department=str(data["department"]).strip(),
            doctor_name=str(data["doctor"]).strip(),
            date=str(data["date"]).strip(),
            time=str(data["time"]).strip()
        )

        return jsonify(make_json_safe(result))

    except Exception as e:
        print("BOOK APPOINTMENT ERROR:", repr(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


###########################################################
# GET APPOINTMENT
###########################################################

@app.route(
    "/api/appointment/<patient_id>",
    methods=["GET"]
)
def get_appointment(patient_id):
    appointment = am.get_appointment(patient_id)
    if appointment:
        return jsonify(make_json_safe(appointment))

    return jsonify({
        "success": False,
        "message": "Appointment not found."
    })

###########################################################
# TODAY APPOINTMENTS
###########################################################

@app.route(
    "/api/today_appointments",
    methods=["GET"]
)
def today_appointments():
    return jsonify(
        make_json_safe(am.get_today_appointments())
    )

###########################################################
# UPDATE PAYMENT STATUS
###########################################################

@app.route(
    "/api/payment_status",
    methods=["PUT"]
)
def payment_status():
    data = request.get_json()
    success = am.update_payment_status(
        data["patient_id"],
        data["status"]
    )

    return jsonify({
        "success": success
    })


###########################################################
# GET DEPARTMENTS
###########################################################

@app.route("/api/departments", methods=["GET"])
def get_departments():
    return jsonify(
        make_json_safe(am.get_departments())
    )

###########################################################
# GET DOCTORS
###########################################################

@app.route("/api/doctors/<department>")
def get_doctors(department):
    return jsonify(
        make_json_safe(am.get_doctors(department))
    )

###########################################################
# GET SCHEDULE
###########################################################

@app.route("/api/schedule/<doctor>")
def get_schedule(doctor):
    return jsonify(
        make_json_safe(am.get_schedule(doctor))
    )


@app.route("/api/consultant_bill/<patient_id>")
def consultant_bill(patient_id):
    return jsonify(
        bm.get_consultant_bill(patient_id)
    )


@app.route("/api/payment_history/<patient_id>")
def payment_history(patient_id):
    return jsonify(
        bm.get_payment_history(patient_id)
    )

@app.route("/api/map/<department>")
def get_map(department):
    return jsonify(
        mm.get_map(department)
    )

@app.route("/api/service_bill/<patient_id>")
def service_bill(patient_id):
    return jsonify(
        bm.get_service_bill(patient_id)
    )

@app.route("/api/faqs")
def get_faqs():
    return jsonify(
        fm.get_all_faqs()
    )

###########################################################
# PRINT RECEIPT (UPDATED TO RECEIVE RAW JSON OR WRAPPED HTML)
###########################################################

@app.route(
    "/api/print_receipt",
    methods=["POST"]
)
def print_receipt():
    try:
        data = request.get_json(silent=True)

        # Fallback to text reading if get_json returns None
        if data is None:
            raw_text = request.get_data(as_text=True)
            content = raw_text.strip() if raw_text else None
        else:
            # Check if payload is wrapped in {"html": ...} or sent as raw dictionary
            content = data.get("html", data)

        if not content:
            return jsonify({
                "success": False,
                "message": "No receipt data received."
            }), 400

        result = printer.print_html(content)

        return jsonify({
            "success": True,
            "message": "Receipt sent to printer.",
            "printer": result.get("printer", ""),
            "job": str(result.get("job", ""))
        })

    except Exception as e:
        print("PRINT ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


###########################################################
# NEO NANO MEDICAL AI
###########################################################

@app.route("/api/neo-nano/status", methods=["GET"])
def neo_nano_status():
    from neo_nano_ai.medical_data_loader import load_master_records
    records = load_master_records()
    return jsonify({
        "success": True,
        "status": "ready" if records else "dataset_not_loaded",
        "knowledge_base_records": len(records),
        "id_range": [records[0]["id"], records[-1]["id"]] if records else []
    })


@app.route("/api/neo-nano/analyze", methods=["POST"])
def neo_nano_analyze():

    data = request.get_json(silent=True) or {}
    symptoms = str(data.get("symptoms", "")).strip()
    symptom_context = data.get("symptom_context") or {}

    if not symptoms:
        return jsonify({
            "success": False,
            "message": "Symptoms required"
        }), 400

    # Keep the patient's structured symptom information with the request.
    # The retriever uses the symptom text for routing; the additional fields
    # are preserved for the voice/conversation layer and clinical review.
    context_parts = [
        symptom_context.get("onset", ""),
        symptom_context.get("duration", ""),
        symptom_context.get("characteristics", ""),
        symptom_context.get("related_symptoms", ""),
    ]
    enriched_query = " ".join(
        [symptoms] + [str(x).strip() for x in context_parts if str(x).strip()]
    ).strip()

    result = analyze(enriched_query, limit=5)

    # disease_retriever returns recommended_departments. The previous code
    # incorrectly looked for result["department"], which caused valid Neo
    # Nano recommendations to fall back to General Medicine.
    recommended_departments = result.get("recommended_departments") or []
    department = (
        recommended_departments[0]
        if recommended_departments
        else "General Medicine"
    )

    # ---------------- Doctors ----------------
    doctors = []

    for _, row in doctors_df.iterrows():

        dept = str(row.get("Department", "")).strip().lower()

        if dept == department.lower():

            doctors.append({
                "name": row.get("Doctor Name", ""),
                "specialization": row.get("Department", "")
            })

    # ---------------- Medical Tests ----------------
    tests = []

    for t in medical_tests:

        dept = str(t.get("department", "")).strip().lower()

        if dept == department.lower():

            tests.append(t.get("test_name"))

    # ---------------- Conditions ----------------
    conditions = []

    for c in result.get("possible_conditions", []):

        name = c.get("name") if isinstance(c, dict) else c
        if name:
            conditions.append(name)

    return jsonify({
        "success": True,
        "department": department,
        "recommended_departments": recommended_departments[:3],
        "confidence": result.get("confidence", 95),
        "reason": result.get(
            "clinical_note",
            "Symptoms require assessment by the selected department."
        ),
        "conditions": conditions,
        "doctors": doctors,
        "tests": tests,
        "symptom_context": symptom_context,
        "triage": result.get("triage", {})
    })

@app.route("/api/neo-nano/departments/<department>/diseases", methods=["GET"])
def neo_nano_department_diseases(department):
    """Return disease records that belong to one Departments.xlsx department."""
    from neo_nano_ai.department_mapper import canonical_department, HOSPITAL_DEPARTMENTS

    canonical = canonical_department(department)
    if not canonical:
        return jsonify({
            "success": False,
            "message": "Unknown department.",
            "available_departments": HOSPITAL_DEPARTMENTS,
        }), 404

    query = request.args.get("query", "")
    limit = max(1, min(int(request.args.get("limit", 50)), 500))

    try:
        diseases = retrieve(query, limit=limit, department=canonical)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    return jsonify({
        "success": True,
        "department": canonical,
        "count": len(diseases),
        "diseases": diseases,
    })


@app.route("/api/neo-nano/knowledge-graph", methods=["GET"])
def neo_nano_knowledge_graph():
    return jsonify({
        "success": True,
        "graph": build_global_graph()
    })

@app.route("/api/neo-nano/genomics/<disease_id>", methods=["GET"])
def neo_nano_genomics(disease_id):
    result = get_genomics(disease_id)
    if result is None:
        return jsonify({"success": False, "message": "Disease not found"}), 404
    result["success"] = True
    return jsonify(result)


###########################################################
# VOICE ASSISTANT
###########################################################
from voice.conversation import ConversationManager
from voice.local_piper_tts import LocalPiperTTS

voice_manager = ConversationManager()
local_tts = LocalPiperTTS()

def _tts_result(result):
    """Attach local Piper audio to a voice result; no cloud voice API."""
    speech = str(result.get("speech") or "").strip()
    if not speech:
        return result
    try:
        result["audio_base64"] = local_tts.audio_base64(speech, result.get("language") or "en-IN")
        result["audio_mime"] = "audio/wav"
    except Exception as exc:
        result["tts_error"] = str(exc)
    return result

@app.route("/api/patients/search", methods=["GET"])
def search_patients():
    q = str(request.args.get("q", "")).strip()
    if not q:
        return jsonify({"success": True, "patients": []})
    ql = q.lower()
    all_patients = pm.get_all_patients()
    matches = []
    for p in all_patients:
        fields = [
            p.get("PATIENT ID", ""), p.get("PATIENT NAME", ""),
            p.get("PHONE", ""), p.get("Patient ID", ""),
            p.get("Patient Name", ""), p.get("Phone", "")
        ]
        if any(ql in str(v).lower() for v in fields):
            matches.append(p)
    return jsonify({"success": True, "patients": make_json_safe(matches[:10])})

@app.route("/api/voice/session", methods=["POST"])
def voice_session():
    data = request.get_json(silent=True) or {}
    lang = data.get("language")
    if lang not in ("en-IN", "ml-IN"):
        lang = None
    s = voice_manager.create(lang)
    # The camera check-in owns the welcome/identity step. Voice sessions created
    # here remain idle until /api/voice/checkin selects existing or new.
    result = voice_manager._result(s, "")
    return jsonify(result)

@app.route("/api/voice/checkin", methods=["POST"])
def voice_checkin():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    mode = data.get("mode")
    s = voice_manager.get(sid)
    if not s or mode not in ("existing", "new"):
        return jsonify({"success": False, "message": "session_id and valid mode are required"}), 400
    try:
        s["camera_checkin"] = True
        # Language is selected on the index page and locked for this visit.
        selected_lang = data.get("language") or s.get("language")
        if selected_lang in ("en-IN", "ml-IN"):
            s["language"] = selected_lang
        if mode == "existing":
            patient = data.get("patient") or {}
            pid = patient.get("PATIENT ID") or patient.get("Patient ID") or patient.get("patient_id")
            if not pid:
                return jsonify({"success": False, "message": "patient_id is required for existing patient"}), 400
            if not patient:
                patient = pm.get_patient_by_id(pid)
            if not patient:
                return jsonify({"success": False, "message": "Patient not found"}), 404
            s["patient"] = patient
            s["patient_id"] = pid
            s["camera_mode"] = "existing"
            s["state"] = "INITIAL_CONCERN"
            s["symptom_index"] = 0
            name = patient.get("PATIENT NAME") or "there"
            speech = voice_manager.say(s, "welcome_back").format(name=name)
            result = voice_manager._result(s, speech, "neo_nano_symptoms.html")
        else:
            s["patient"] = None
            s["patient_id"] = None
            s["camera_mode"] = "new"
            s["state"] = "REG_NAME"
            s["symptom_index"] = 0
            speech = voice_manager.say(s, "new_patient")
            result = voice_manager._result(s, speech, "new_patient.html")
        result["success"] = True
        _tts_result(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/voice/text", methods=["POST"])
def voice_text():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    text = str(data.get("text", "")).strip()
    if not sid or not text:
        return jsonify({"success": False, "message": "session_id and text are required"}), 400
    try:
        result = voice_manager.text(sid, text)
        result["success"] = True
        _tts_result(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/voice/audio", methods=["POST"])
def voice_audio():
    return jsonify({"success": False, "message": "Patient voice input is disabled for the touchscreen-first demo."}), 410

@app.route("/api/voice/tts", methods=["POST"])
def voice_tts():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    language = data.get("language", "en-IN")
    if not text:
        return jsonify({"success": False, "message": "text required"}), 400
    if language not in ("en-IN", "ml-IN"):
        language = "en-IN"
    try:
        audio = local_tts.audio_base64(text, language)
        return jsonify({"success": True, "audio_base64": audio, "audio_mime": "audio/wav"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 502


@app.route("/api/voice/bind-patient", methods=["POST"])
def voice_bind_patient():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    patient = data.get("patient")
    s = voice_manager.get(sid)
    if not s or not isinstance(patient, dict):
        return jsonify({"success": False, "message": "Invalid voice session or patient"}), 400
    s["patient"] = patient
    s["patient_id"] = patient.get("PATIENT ID") or patient.get("Patient ID") or patient.get("patient_id")
    s["camera_checkin"] = True
    s["camera_mode"] = "new" if s.get("camera_mode") == "new" else s.get("camera_mode")
    s["state"] = "INITIAL_CONCERN"
    s["symptom_index"] = 1 if s.get("initial_concern") else 0
    name = patient.get("PATIENT NAME", "there")
    speech = voice_manager.say(s, "new_registered").format(name=name) if s.get("camera_mode") == "new" else voice_manager.say(s, "welcome_back").format(name=name)
    result = voice_manager._result(s, speech, "neo_nano_symptoms.html")
    result["success"] = True
    _tts_result(result)
    return jsonify(result)

@app.route("/api/voice/sync-appointment", methods=["POST"])
def voice_sync_appointment():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    ap = data.get("appointment") or {}
    s = voice_manager.get(sid)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    s["appointment"] = ap
    s["patient_id"] = s.get("patient_id") or ap.get("Patient ID")
    s["department"] = ap.get("Department") or s.get("department")
    s["doctor"] = ap.get("Doctor") or s.get("doctor")
    s["date"] = ap.get("Date") or s.get("date")
    s["time"] = ap.get("Time") or s.get("time")
    s["state"] = "DASHBOARD"
    result = voice_manager._result(s, voice_manager.say(s, "booked").format(department=s["department"], doctor=s["doctor"], date=s["date"], time=s["time"]), "dashboard.html")
    result["success"] = True
    _tts_result(result)
    return jsonify(result)

@app.route("/api/voice/manual-sync", methods=["POST"])
def voice_manual_sync():
    """Synchronize visible touchscreen fields into the active voice session.
    Touch input wins for fields the patient edits manually, so the voice layer
    continues from the first field that is still missing instead of asking for
    a field that was already entered on the touchscreen.
    """
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    page = str(data.get("page") or "").strip()
    fields = data.get("fields") or {}
    s = voice_manager.get(sid)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    if not isinstance(fields, dict):
        return jsonify({"success": False, "message": "fields must be an object"}), 400

    if page == "new_patient":
        mapping = {
            "patientName": "PATIENT NAME", "patientDob": "DATE OF BIRTH",
            "patientAge": "AGE", "patientPhone": "PHONE",
            "patientEmail": "EMAIL", "patientAddress": "ADDRESS",
        }
        for eid, key in mapping.items():
            if str(fields.get(eid, "")).strip() != "":
                s["patient_draft"][key] = fields[eid]
        if s["patient_draft"].get("DATE OF BIRTH") and not s["patient_draft"].get("AGE"):
            try:
                dob = date.fromisoformat(str(s["patient_draft"]["DATE OF BIRTH"])[:10])
                today = date.today()
                s["patient_draft"]["AGE"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except Exception:
                pass
        required = [
            ("REG_NAME", "PATIENT NAME"), ("REG_PHONE", "PHONE"),
            ("REG_DOB", "DATE OF BIRTH"), ("REG_EMAIL", "EMAIL"),
            ("REG_ADDRESS", "ADDRESS")
        ]
        missing = next((state for state, key in required if not str(s["patient_draft"].get(key, "")).strip()), None)
        s["state"] = missing or "INITIAL_CONCERN"

    elif page == "neo_nano":
        mapping = {
            "symptoms": "symptoms", "onset": "onset", "duration": "duration",
            "prior_occurrence": "prior_occurrence", "characteristics": "characteristics",
            "severity": "severity", "trend": "trend", "related_symptoms": "related_symptoms",
            "aggravating_relief": "aggravating_relief", "medications": "medications",
            "allergies": "allergies", "last_doctor_visit": "last_doctor_visit", "previous_condition": "previous_condition"
        }
        for eid, key in mapping.items():
            if str(fields.get(eid, "")).strip() != "":
                s["symptom_context"][key] = fields[eid]
        if str(fields.get("symptoms", "")).strip():
            s["initial_concern"] = str(fields["symptoms"]).strip()
        checks = [(i, key) for i, key in enumerate(["symptoms","onset","duration","prior_occurrence","characteristics","severity","trend","related_symptoms","aggravating_relief","medications","allergies","last_doctor_visit","previous_condition"])]
        missing_index = next((idx for idx, key in checks if not str(s["symptom_context"].get(key, "")).strip()), len(checks))
        s["symptom_index"] = missing_index
        s["state"] = "NEO_ANALYZE" if missing_index >= len(checks) else ("INITIAL_CONCERN" if missing_index == 0 else "SYMPTOM_INTAKE")

    elif page == "appointments":
        if str(fields.get("department", "")).strip(): s["department"] = str(fields["department"]).strip()
        if str(fields.get("doctor", "")).strip(): s["doctor"] = str(fields["doctor"]).strip()
        if str(fields.get("appointmentDate", "")).strip(): s["date"] = str(fields["appointmentDate"]).strip()
        if str(fields.get("opdTime", "")).strip() and str(fields["opdTime"]).strip() not in {"Select OPD Time", "No Time Available"}: s["time"] = str(fields["opdTime"]).strip()
        if not s.get("department"): s["state"] = "APPT_DEPARTMENT"
        elif not s.get("doctor"): s["state"] = "APPT_DOCTOR"
        elif not s.get("date"): s["state"] = "APPT_DATE"
        elif not s.get("time"): s["state"] = "APPT_TIME"
        else: s["state"] = "APPT_CONFIRM"

    return jsonify({"success": True, "state": s.get("state"), "autofill": voice_manager._autofill(s)})

@app.route("/api/voice/state/<session_id>", methods=["GET"])
def voice_state(session_id):
    s = voice_manager.get(session_id)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    return jsonify(voice_manager._result(s, ""))

@app.route("/api/voice/advance", methods=["POST"])
def voice_advance():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    s = voice_manager.get(sid)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    try:
        if s["state"] == "LANGUAGE_SELECTION":
            result = voice_manager._result(s, voice_manager._language_prompt(s))
        elif s["state"] == "DASHBOARD":
            result = voice_manager._load_bill(s)
        elif s["state"] == "BILLING":
            result = voice_manager._load_bill(s)
        else:
            result = voice_manager._result(s, "")
        result["success"] = True
        _tts_result(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def _print_voice_payment_receipt(session_data, method):
    """Print the consultant payment receipt before continuing to wayfinding.

    Printing is deliberately best-effort: a printer failure must not block the
    patient's completed payment workflow or the transition to wayfinding.
    """
    now = datetime.now()
    patient = session_data.get("patient") or {}
    appointment = session_data.get("appointment") or {}
    bill = session_data.get("bill") or {}

    receipt = {
        "receiptNo": f"RCPT-{now.strftime('%Y%m%d%H%M%S')}",
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%I:%M:%S %p"),
        "patientId": patient.get("PATIENT ID") or session_data.get("patient_id", ""),
        "patientName": patient.get("PATIENT NAME", ""),
        "appointmentId": appointment.get("Appointment ID") or bill.get("Appointment ID", ""),
        "token": appointment.get("Token") or bill.get("Token", "A-001"),
        "consultant": bill.get("Consultant") or appointment.get("Doctor") or session_data.get("doctor", ""),
        "amount": bill.get("Total") or bill.get("total") or bill.get("Amount") or bill.get("amount") or 0,
        "paymentMethod": method,
        "status": "PAID",
    }

    # Printing is performed by frontend/pages/receipt.html so the workflow
    # visibly passes through the dedicated printing page before wayfinding.
    return {
        "success": True,
        "receipt": receipt,
    }


@app.route("/api/voice/payment-complete", methods=["POST"])
def voice_payment_complete():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    s = voice_manager.get(sid)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    method = data.get("method") or s.get("payment_method")
    if method:
        s["payment_method"] = method
    try:
        if s["payment_method"] in ("UPI", "Card"):
            voice_manager.hms.payment_status(s["patient_id"], "Paid")

        # Build the receipt data and open the dedicated printing page.
        # The printing page sends the receipt to the thermal printer exactly once.
        print_result = _print_voice_payment_receipt(s, s["payment_method"])
        s["receipt"] = print_result.get("receipt")
        # The visible receipt page is a printing step, but the next voice state
        # is already wayfinding so the patient's "thank you" is handled there.
        s["state"] = "WAYFINDING"
        s["wayfinding"] = voice_manager.hms.map(s.get("department", "")) or {}
        result = voice_manager._result(s, "Payment completed. Your receipt is being prepared.", "receipt.html")
        result["success"] = True
        result["receipt"] = print_result.get("receipt")
        _tts_result(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/voice/cash", methods=["POST"])
def voice_cash():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    s = voice_manager.get(sid)
    if not s:
        return jsonify({"success": False, "message": "Unknown voice session"}), 404
    s["payment_method"] = "Cash"

    # Build receipt data and open the dedicated printing page.
    print_result = _print_voice_payment_receipt(s, "Cash")
    s["receipt"] = print_result.get("receipt")
    s["state"] = "WAYFINDING"
    s["wayfinding"] = voice_manager.hms.map(s.get("department", "")) or {}
    result = voice_manager._result(s, "Cash payment confirmed. Your receipt is being prepared.", "receipt.html")
    result["success"] = True
    result["receipt"] = print_result.get("receipt")
    _tts_result(result)
    return jsonify(result)

@app.route("/api/voice/end", methods=["POST"])
def voice_end():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    if sid in voice_manager.sessions:
        voice_manager.sessions.pop(sid, None)
    return jsonify({"success": True})


###########################################################
# FACE CHECK-IN
###########################################################

@app.route("/api/face/status", methods=["GET"])
def face_status():
    """Return only the backend camera recognition state; no camera access in browser."""
    try:
        start_camera()
    except Exception:
        pass
    result = camera_status()
    if result.get("recognized"):
        patient_id = result.get("patient_id")
        patient = pm.get_patient_by_id(patient_id)
        if patient:
            result["patient"] = make_json_safe(patient)
        else:
            result["recognized"] = False
            result["message"] = "Patient record not found."
    return jsonify({"success": True, **result})

@app.route("/api/face/identify", methods=["POST"])
def face_identify():
    """Compatibility endpoint for server-side integrations that send an image."""
    if "image" not in request.files:
        return jsonify({"success": False, "message": "image is required"}), 400
    try:
        result = identify_face(request.files["image"].read())
        if result.get("recognized"):
            patient_id = result.get("patient_id")
            patient = pm.get_patient_by_id(patient_id)
            if not patient:
                result["recognized"] = False
            else:
                result["patient"] = make_json_safe(patient)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 503

@app.route("/api/face/enroll", methods=["POST"])
def face_enroll():
    """Compatibility endpoint; browser camera is no longer used by the HMS UI."""
    patient_id = str(request.form.get("patient_id", "")).strip()
    if not patient_id or "image" not in request.files:
        return jsonify({"success": False, "message": "patient_id and image are required"}), 400
    try:
        result = enroll_face(patient_id, request.files["image"].read())
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/face/enroll-from-camera", methods=["POST"])
def face_enroll_from_camera():
    patient_id = str(request.form.get("patient_id", "")).strip()
    if not patient_id:
        return jsonify({"success": False, "message": "patient_id is required"}), 400
    try:
        result = enroll_from_camera(patient_id)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

###########################################################
# FRONTEND PAGES
###########################################################

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)
PAGES_DIR = os.path.join(FRONTEND_DIR, "pages")

@app.route("/pages/<path:filename>")
def serve_pages(filename):
    return send_from_directory(PAGES_DIR, filename)

@app.route("/neo")
def neo():
    return send_from_directory(PAGES_DIR, "neo_nano_welcome.html")

# Serve root-level frontend assets (JS, CSS, images, language files, menu.html, etc.)
# without exposing the camera to the browser. API routes above remain unchanged.
@app.route("/<path:filename>")
def serve_frontend_asset(filename):
    # Never let this catch-all handle API requests.
    if filename == "api" or filename.startswith("api/"):
        return jsonify({"success": False, "message": "Not found"}), 404
    target = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(target):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"success": False, "message": "Not found"}), 404


if __name__ == "__main__":
    # The camera belongs exclusively to the backend. Disable Flask's debug
    # reloader so two processes never compete for /dev/video2.
    start_camera()
    app.run(host="0.0.0.0", port=5000, debug=False)
