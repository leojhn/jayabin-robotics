from flask import Blueprint,jsonify,request

from patient_manager import PatientManager

patient_api = Blueprint(

    "patient",

    __name__

)

manager = PatientManager()

######################################################

@patient_api.route("/patients")

def patients():

    return jsonify(

        manager.get_all_patients()

    )

######################################################

@patient_api.route("/patient/<patient_id>")

def patient(patient_id):

    data = manager.search_patient(

        patient_id

    )

    if data:

        return jsonify(data)

    return jsonify({

        "error":"Patient not found"

    })

######################################################

@patient_api.route(

    "/register",

    methods=["POST"]

)

def register():

    data = request.json

    manager.register_patient(data)

    return jsonify({

        "status":"success"

    })