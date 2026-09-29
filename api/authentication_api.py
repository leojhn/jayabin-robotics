from flask import Blueprint,jsonify

from authentication import Authentication

auth_api = Blueprint(

    "auth",

    __name__

)

auth = Authentication()

@auth_api.route("/authenticate")

def authenticate():

    return jsonify(

        auth.authenticate()

    )