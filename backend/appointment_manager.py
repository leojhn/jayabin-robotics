import pandas as pd
from datetime import datetime

from excel_loader import db
from config import APPOINTMENT_FILE


class AppointmentManager:

    ########################################################
    # Constructor
    ########################################################

    def __init__(self):
        self.reload()

    ########################################################
    # Reload Database
    ########################################################

    def reload(self):

        db.reload()

        self.appointments = db.appointments
        self.patients = db.patients
        self.doctors = db.doctors
        self.consultants = db.consultants
        self.schedule = db.schedule

        # Keep old and new appointment Excel files compatible.
        required_columns = {
            "Appointment ID": "",
            "Patient ID": "",
            "Patient Name": "",
            "Gender": "",
            "Age": "",
            "Department": "",
            "Doctor": "",
            "Doctor ID": "",
            "Consultation Fee": 0,
            "Token": "",
            "Date": "",
            "Time": "",
            "Status": "Confirmed",
            "Payment Status": "Pending",
        }

        for column, default in required_columns.items():
            if column not in self.appointments.columns:
                self.appointments[column] = default

    ########################################################
    # Save Appointment File
    ########################################################

    def save(self):

        self.appointments.to_excel(
            APPOINTMENT_FILE,
            index=False,
            engine="openpyxl"
        )

        db.reload()
        self.reload()

    ########################################################
    # APPOINTMENT ID GENERATOR
    ########################################################

    def generate_appointment_id(self):

        self.reload()

        if self.appointments.empty:
            return "AP-001"

        ids = []

        for value in self.appointments["Appointment ID"]:

            try:

                value = str(value).strip().upper()

                if value.startswith("AP-"):

                    ids.append(
                        int(
                            value.replace("AP-", "")
                        )
                    )

            except Exception:
                continue

        if not ids:
            return "AP-001"

        return f"AP-{max(ids)+1:03d}"


    ########################################################
    # TOKEN GENERATOR
    ########################################################

    def generate_token(self, department):

        self.reload()

        department = str(department).strip()

        appointments = self.appointments[
            self.appointments["Department"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            department.lower()
        ]

        prefix = department[:1].upper()

        if appointments.empty:
            return f"{prefix}001"

        tokens = []

        for token in appointments["Token"]:

            try:

                token = str(token).strip().upper()

                if token.startswith(prefix):

                    tokens.append(
                        int(
                            token[1:]
                        )
                    )

            except Exception:
                continue

        if not tokens:
            return f"{prefix}001"

        return f"{prefix}{max(tokens)+1:03d}"
        ########################################################
    # CONSULTATION FEE
    ########################################################

    def get_consultation_fee(self, doctor_name):

        self.reload()

        doctor_name = str(doctor_name).strip()

        consultant = self.consultants[

            self.consultants["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            doctor_name.lower()

        ]

        if consultant.empty:
            return 0.0

        try:

            fee = consultant.iloc[0]["Consultation Charge"]

            if pd.isna(fee):
                return 0.0

            return float(fee)

        except Exception:

            return 0.0

        ########################################################
    # BOOK APPOINTMENT
    ########################################################

    def book_appointment(
        self,
        patient_id,
        department,
        doctor_name,
        date,
        time
    ):

        self.reload()

        ####################################################
        # Validate Patient
        ####################################################

        patient = self.patients[
            self.patients["PATIENT ID"]
            .astype(str)
            .str.strip()
            .str.upper()
            ==
            str(patient_id).strip().upper()
        ]

        if patient.empty:

            return {
                "success": False,
                "message": "Patient not found."
            }

        patient = patient.iloc[0]

        ####################################################
        # Validate Doctor
        ####################################################

        doctor = self.doctors[
            self.doctors["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(doctor_name).strip().lower()
        ]

        if doctor.empty:

            return {
                "success": False,
                "message": "Doctor not found."
            }

        doctor = doctor.iloc[0]

        ####################################################
        # Check Duplicate Appointment
        ####################################################

        duplicate = self.appointments[
            (
                self.appointments["Patient ID"]
                .astype(str)
                .str.strip()
                .str.upper()
                ==
                str(patient_id).strip().upper()
            )
            &
            (
                self.appointments["Date"]
                .astype(str)
                .str.strip()
                ==
                str(date).strip()
            )
        ]

        if not duplicate.empty:

            return {
                "success": False,
                "message": "This patient already has an appointment on the selected date."
            }

        ####################################################
        # Check Time Slot Availability
        ####################################################

        booked = self.appointments[

            (self.appointments["Doctor"]
             .astype(str)
             .str.lower()
             ==
             str(doctor_name).lower())

            &

            (self.appointments["Date"]
             .astype(str)
             ==
             str(date))

            &

            (self.appointments["Time"]
             .astype(str)
             ==
             str(time))
        ]

        if not booked.empty:

            return {
                "success": False,
                "message": "Selected time slot is already booked."
            }

        ####################################################
        # Generate Appointment Details
        ####################################################

        appointment_id = self.generate_appointment_id()

        token = self.generate_token(
            department
        )

        consultation_fee = self.get_consultation_fee(
            doctor_name
        )

        ####################################################
        # Create Appointment
        ####################################################

        appointment = {

            "Appointment ID": appointment_id,

            "Patient ID": str(patient.get("PATIENT ID", patient_id)).strip(),

            "Patient Name": str(patient.get("PATIENT NAME", "")).strip(),

            "Gender": str(patient.get("GENDER", patient.get("Gender", "")) or "").strip(),

            "Age": str(patient.get("AGE", patient.get("Age", "")) or "").strip(),

            "Department": str(department).strip(),

            "Doctor": str(doctor_name).strip(),

            "Doctor ID": str(doctor.get("Doctor ID", "")).strip(),

            "Consultation Fee": float(consultation_fee or 0),

            "Token": str(token).strip(),

            "Date": str(date).strip(),

            "Time": str(time).strip(),

            "Status": "Confirmed",

            "Payment Status": "Pending",

        }

        ####################################################
        # Save Appointment
        ####################################################

        self.appointments = pd.concat(

            [
                self.appointments,
                pd.DataFrame([appointment])
            ],

            ignore_index=True

        )

        self.save()

        ####################################################
        # Response
        ####################################################

        return {

            "success": True,

            "message": "Appointment booked successfully.",

            "appointment": appointment

        }
        ########################################################
    # GET APPOINTMENT
    ########################################################

    def get_appointment(self, patient_id):

        self.reload()

        patient_id = str(patient_id).strip().upper()

        appointments = self.appointments[
            self.appointments["Patient ID"]
            .astype(str)
            .str.strip()
            .str.upper()
            == patient_id
        ]

        if appointments.empty:
            return None

        appointments = appointments.sort_values(
            by="Appointment ID",
            kind="stable"
        )

        latest = appointments.iloc[-1]

        def value(name, default=""):
            result = latest.get(name, default)

            if pd.isna(result):
                return default

            return result

        fee = value("Consultation Fee", 0)

        try:
            fee = float(fee)
        except Exception:
            fee = 0.0

        return {

            "Appointment ID": str(value("Appointment ID")),
            "Patient ID": str(value("Patient ID")),
            "Patient Name": str(value("Patient Name")),
            "Gender": str(value("Gender")),
            "Age": str(value("Age")),
            "Department": str(value("Department")),
            "Doctor": str(value("Doctor")),
            "Doctor ID": str(value("Doctor ID")),
            "Consultation Fee": fee,
            "Token": str(value("Token")),
            "Date": str(value("Date")),
            "Time": str(value("Time")),
            "Status": str(value("Status", "Confirmed")),
            "Payment Status": str(value("Payment Status", "Pending"))

        }

    ########################################################
    # TODAY APPOINTMENTS
    ########################################################

    def get_today_appointments(self):

        self.reload()

        ####################################################
        # Today's Date
        ####################################################

        today = datetime.now().strftime("%d-%m-%Y")

        ####################################################
        # Filter Today's Appointments
        ####################################################

        appointments = self.appointments[

            self.appointments["Date"]
            .astype(str)
            .str.strip()

            ==

            today

        ]

        ####################################################
        # No Appointments
        ####################################################

        if appointments.empty:

            return []

        ####################################################
        # Sort by Time
        ####################################################

        try:

            appointments = appointments.sort_values(

                by="Time"

            )

        except Exception:

            pass

        ####################################################
        # Convert NaN Values
        ####################################################

        appointments = appointments.fillna("")

        ####################################################
        # Return Records
        ####################################################

        return appointments.to_dict(

            orient="records"

        )
        ########################################################
    # UPDATE PAYMENT STATUS
    ########################################################

    def update_payment_status(
        self,
        patient_id,
        status="Paid"
    ):

        self.reload()

        ####################################################
        # Find Latest Appointment
        ####################################################

        appointments = self.appointments[

            self.appointments["Patient ID"]
            .astype(str)
            .str.strip()
            .str.upper()

            ==

            str(patient_id).strip().upper()

        ]

        ####################################################
        # Patient Not Found
        ####################################################

        if appointments.empty:

            return False

        ####################################################
        # Latest Appointment Index
        ####################################################

        latest_index = appointments.index[-1]

        ####################################################
        # Update Status
        ####################################################

        self.appointments.loc[
            latest_index,
            "Payment Status"
        ] = status

        ####################################################
        # Save Changes
        ####################################################

        self.save()

        ####################################################
        # Success
        ####################################################

        return True
        ########################################################
    # GET DEPARTMENTS
    ########################################################

    def get_departments(self):

        self.reload()

        ####################################################
        # Doctors Database Empty
        ####################################################

        if self.doctors.empty:

            return []

        ####################################################
        # Department Column Exists
        ####################################################

        if "Department" not in self.doctors.columns:

            return []

        ####################################################
        # Get Unique Departments
        ####################################################

        departments = (

            self.doctors["Department"]

            .dropna()

            .astype(str)

            .str.strip()

            .replace("", pd.NA)

            .dropna()

            .unique()

        )

        ####################################################
        # Sort Alphabetically
        ####################################################

        departments = sorted(departments)

        ####################################################
        # Return JSON
        ####################################################

        return [

            {
                "Department": department
            }

            for department in departments

        ]
        ########################################################
    # GET DOCTORS
    ########################################################

    def get_doctors(self, department):

        self.reload()

        ####################################################
        # Validate Input
        ####################################################

        department = str(department).strip()

        if department == "":
            return []

        ####################################################
        # Doctors Database Empty
        ####################################################

        if self.doctors.empty:
            return []

        ####################################################
        # Required Columns
        ####################################################

        required_columns = [
            "Doctor ID",
            "Doctor Name",
            "Department"
        ]

        for column in required_columns:

            if column not in self.doctors.columns:
                return []

        ####################################################
        # Filter Department
        ####################################################

        doctors = self.doctors[

            self.doctors["Department"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            department.lower()

        ]

        ####################################################
        # No Doctors
        ####################################################

        if doctors.empty:
            return []

        ####################################################
        # Remove Duplicate Doctors
        ####################################################

        doctors = doctors.drop_duplicates(

            subset=["Doctor ID"]

        )

        ####################################################
        # Sort by Doctor Name
        ####################################################

        doctors = doctors.sort_values(

            by="Doctor Name"

        )

        ####################################################
        # Replace NaN
        ####################################################

        doctors = doctors.fillna("")

        ####################################################
        # Return JSON
        ####################################################

        return doctors.to_dict(

            orient="records"

        )
        ########################################################
    # GET DOCTOR SCHEDULE
    ########################################################

    def get_schedule(self, doctor):

        self.reload()

        ####################################################
        # Validate Input
        ####################################################

        doctor = str(doctor).strip()

        if doctor == "":
            return []

        ####################################################
        # Schedule Database Empty
        ####################################################

        if self.schedule.empty:
            return []

        ####################################################
        # Required Columns
        ####################################################

        required_columns = [
            "Doctor Name",
            "OPD Time"
        ]

        for column in required_columns:

            if column not in self.schedule.columns:
                return []

        ####################################################
        # Filter Doctor
        ####################################################

        schedule = self.schedule[

            self.schedule["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            doctor.lower()

        ]

        ####################################################
        # Doctor Not Found
        ####################################################

        if schedule.empty:
            return []

        ####################################################
        # Remove Duplicate Entries
        ####################################################

        schedule = schedule.drop_duplicates()

        ####################################################
        # Sort (Optional)
        ####################################################

        if "Day" in schedule.columns:

            schedule = schedule.sort_values(
                by="Day"
            )

        ####################################################
        # Replace NaN
        ####################################################

        schedule = schedule.fillna("")

        ####################################################
        # Return JSON
        ####################################################

        return schedule.to_dict(
            orient="records"
        )
        ########################################################
    # CHECK TIME SLOT AVAILABILITY
    ########################################################

    def is_time_slot_available(
        self,
        doctor_name,
        appointment_date,
        appointment_time
    ):

        self.reload()

        ####################################################
        # Validate Input
        ####################################################

        doctor_name = str(doctor_name).strip().lower()
        appointment_date = str(appointment_date).strip()
        appointment_time = str(appointment_time).strip()

        ####################################################
        # Empty Database
        ####################################################

        if self.appointments.empty:
            return True

        ####################################################
        # Filter Matching Appointments
        ####################################################

        booked = self.appointments[

            (
                self.appointments["Doctor"]
                .astype(str)
                .str.strip()
                .str.lower()

                ==

                doctor_name
            )

            &

            (
                self.appointments["Date"]
                .astype(str)
                .str.strip()

                ==

                appointment_date
            )

            &

            (
                self.appointments["Time"]
                .astype(str)
                .str.strip()

                ==

                appointment_time
            )

            &

            (
                self.appointments["Status"]
                .astype(str)
                .str.strip()
                .str.lower()

                !=

                "cancelled"
            )

        ]

        ####################################################
        # Slot Already Booked
        ####################################################

        if not booked.empty:

            return False

        ####################################################
        # Slot Available
        ####################################################

        return True
        ########################################################
    # PATIENT EXISTS
    ########################################################

    def patient_exists(self, patient_id):

        self.reload()

        if self.patients.empty:
            return False

        patient_id = str(patient_id).strip().upper()

        return (

            self.patients["Patient ID"]
            .astype(str)
            .str.strip()
            .str.upper()

            ==

            patient_id

        ).any()
        ########################################################
    # DOCTOR EXISTS
    ########################################################

    def doctor_exists(self, doctor_name):

        self.reload()

        if self.doctors.empty:
            return False

        doctor_name = str(doctor_name).strip().lower()

        return (

            self.doctors["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            doctor_name

        ).any()
        ########################################################
    # VALIDATE DATE
    ########################################################

    def validate_date(self, appointment_date):

        try:

            datetime.strptime(
                appointment_date,
                "%d-%m-%Y"
            )

            return True

        except ValueError:

            return False

        ########################################################
    # GET PATIENT DETAILS
    ########################################################

    def get_patient(self, patient_id):

        self.reload()

        patient = self.patients[

            self.patients["Patient ID"]
            .astype(str)
            .str.strip()
            .str.upper()

            ==

            str(patient_id).strip().upper()

        ]

        if patient.empty:
            return None

        return patient.iloc[0].to_dict()
        ########################################################
    # GET DOCTOR DETAILS
    ########################################################

    def get_doctor(self, doctor_name):

        self.reload()

        doctor = self.doctors[

            self.doctors["Doctor Name"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            str(doctor_name).strip().lower()

        ]

        if doctor.empty:
            return None

        return doctor.iloc[0].to_dict()
