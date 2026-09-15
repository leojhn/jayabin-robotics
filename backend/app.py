from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import date, datetime
from numbers import Integral, Real


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


from patient_manager import PatientManager
from appointment_manager import AppointmentManager
from billing_manager import BillingManager
from map_manager import MapManager
from faq_manager import FAQManager
from printer import printer
from neo_nano_ai.disease_retriever import analyze
from neo_nano_ai.knowledge_graph_service import build_global_graph
from neo_nano_ai.genomics_service import get_genomics

bm = BillingManager()
am = AppointmentManager()
mm = MapManager()
fm = FAQManager()
app = Flask(__name__)

CORS(app)

pm = PatientManager()

###########################################################

@app.route("/")
def home():
    return jsonify({
        "Hospital": "City Hospital",
        "Version": "1.0",
        "Backend": "Running"
    })

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
    query = str(data.get("query", "")).strip()

    if not query:
        return jsonify({
            "success": False,
            "message": "A symptom description or medical question is required."
        }), 400

    result = analyze(query, limit=int(data.get("limit", 5)))
    result["success"] = True
    return jsonify(result)

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


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
