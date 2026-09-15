import pandas as pd

from excel_loader import db
from config import CONSULTANT_BILLING_FILE


class BillingManager:

    ####################################################
    # Constructor
    ####################################################

    def __init__(self):

        self.reload()

    ####################################################
    # Reload All Excel Files
    ####################################################

    def reload(self):

        db.reload()

        self.consultant_bill = db.consultant_billing

        self.consultants = db.consultants

        self.service_bill = db.service_billing

        self.services = db.services

        self.appointments = db.appointments

            ####################################################
    # Save Consultant Billing
    ####################################################

    def save_consultant_bill(self):

        self.consultant_bill.to_excel(

            CONSULTANT_BILLING_FILE,

            index=False

        )

        ####################################################
    # Get Latest Appointment
    ####################################################

    def get_patient_appointment(self, patient_id):

        self.reload()

        patient = self.appointments[

            self.appointments["Patient ID"]
            .astype(str)
            .str.upper()

            ==

            str(patient_id).upper()

        ]

        if patient.empty:

            return None

        patient = patient.sort_values(

            by="Appointment ID"

        )

        return patient.iloc[-1]

        ####################################################
    # Create Consultant Bill
    ####################################################

    def create_consultant_bill(self, patient_id):

        self.reload()

        appointment = self.get_patient_appointment(patient_id)

        if appointment is None:

            return None

        doctor = str(
            appointment["Doctor"]
        ).strip()

        consultant = self.consultants[

            self.consultants["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            doctor.lower()

        ]

        consultation_charge = 0

        if not consultant.empty:

            consultation_charge = float(

                consultant.iloc[0][
                    "Consultation Charge"
                ]

            )
        if "Appointment ID" not in self.consultant_bill.columns:
            self.consultant_bill["Appointment ID"] = ""

        existing = self.consultant_bill[

            self.consultant_bill["Appointment ID"]
            .astype(str)

            ==

            str(
                appointment["Appointment ID"]
            )

        ]

        if existing.empty:

            new_bill = {

                "Appointment ID":
                appointment["Appointment ID"],

                "Patient ID":
                appointment["Patient ID"],

                "Patient Name":
                appointment["Patient Name"],

                "Department":
                appointment["Department"],

                "Consultant":
                doctor,

                "Date":
                appointment["Date"],

                "Time":
                appointment["Time"],

                "Token":
                appointment["Token"],

                "Consultation Charge":
                consultation_charge,

                "Payment Status":
                "Pending"

            }

            self.consultant_bill = pd.concat(

                [

                    self.consultant_bill,

                    pd.DataFrame([new_bill])

                ],

                ignore_index=True

            )

            self.save_consultant_bill()

            return new_bill

        return existing.iloc[0].to_dict()

        ####################################################
    # Get Consultant Bill
    ####################################################

    def get_consultant_bill(self, patient_id):

        self.reload()

        # Create bill automatically if it doesn't exist
        self.create_consultant_bill(patient_id)

        patient_bill = self.consultant_bill[

            self.consultant_bill["Patient ID"]
            .astype(str)
            .str.upper()

            ==

            str(patient_id).upper()

        ]

        if patient_bill.empty:

            return None

        # Return latest bill
        row = patient_bill.iloc[-1]

        return {

            "Appointment ID":
            row["Appointment ID"],

            "Patient ID":
            row["Patient ID"],

            "Patient Name":
            row["Patient Name"],

            "Department":
            row["Department"],

            "Consultant":
            row["Consultant"],

            "Date":
            row["Date"],

            "Time":
            row["Time"],

            "Token":
            row["Token"],

            "Consultation Charge":
            float(row["Consultation Charge"]),

            "Payment Status":
            row["Payment Status"],

            "Total":
            float(row["Consultation Charge"])

        }

        ####################################################
    # SERVICE BILL
    ####################################################

    def get_service_bill(self, patient_id):

        self.reload()

        patient = self.service_bill[

            self.service_bill["Patient ID"]
            .astype(str)
            .str.upper()

            ==

            str(patient_id).upper()

        ]

        if patient.empty:

            return {

                "Patient ID": patient_id,

                "Patient Name": "",

                "Consultant": "",

                "Services": [],

                "Total": 0

            }

        row = patient.iloc[-1]

        services = []

        total = 0

        service_names = str(

            row["Services"]

        ).split(",")

        for service in service_names:

            service = service.strip()

            service_data = self.services[

                self.services["Services"]
                .astype(str)
                .str.strip()

                ==

                service

            ]

            if service_data.empty:

                amount = 0

            else:

                amount = float(

                    service_data.iloc[0]["Charges"]

                )

            services.append({

                "Service": service,

                "Amount": amount

            })

            total += amount

        return {

            "Patient ID":
            row["Patient ID"],

            "Patient Name":
            row["Patient Name"],

            "Consultant":
            row["Consultant"],

            "Services":
            services,

            "Total":
            total

        }

        ####################################################
    # PAYMENT HISTORY
    ####################################################

    def get_payment_history(self, patient_id):

        self.reload()

        history = []

        ################################################
        # Consultation Bill
        ################################################

        consultant = self.get_consultant_bill(patient_id)

        if consultant is not None:

            history.append({

                "Type": "Consultation",

                "Appointment ID":
                consultant["Appointment ID"],

                "Description":
                consultant["Consultant"],

                "Date":
                consultant["Date"],

                "Time":
                consultant["Time"],

                "Amount":
                consultant["Total"],

                "Status":
                consultant["Payment Status"]

            })

        ################################################
        # Service Bill
        ################################################

        service = self.get_service_bill(patient_id)

        for item in service["Services"]:

            history.append({

                "Type": "Service",

                "Appointment ID":
                consultant["Appointment ID"]
                if consultant else "",

                "Description":
                item["Service"],

                "Date":
                consultant["Date"]
                if consultant else "",

                "Time":
                consultant["Time"]
                if consultant else "",

                "Amount":
                item["Amount"],

                "Status":
                "Pending"

            })

        ################################################
        # Sort by Date and Time
        ################################################

        history = sorted(

            history,

            key=lambda x: (

                x["Date"],

                x["Time"]

            )

        )

        return history


        ####################################################
    # UPDATE PAYMENT STATUS
    ####################################################

    def update_payment_status(

        self,

        patient_id,

        status="Paid"

    ):

        self.reload()

        index = self.consultant_bill[

            self.consultant_bill["Patient ID"]
            .astype(str)
            .str.upper()

            ==

            str(patient_id).upper()

        ].index

        if len(index) == 0:

            return False

        self.consultant_bill.loc[

            index[-1],

            "Payment Status"

        ] = status

        self.save_consultant_bill()

        return True
        ####################################################
    # GET TOTAL BILL
    ####################################################

    def get_total_bill(self, patient_id):

        consultant = self.get_consultant_bill(

            patient_id

        )


        consultant_total = 0

        if consultant:

            consultant_total = consultant["Total"]



        return {

            "Consultation":

            consultant_total,


            "Grand Total":

            consultant_total

        }
    ####################################################
# Billing Manager Object
####################################################

billing_manager = BillingManager()
