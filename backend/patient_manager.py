import pandas as pd

from excel_loader import db
from config import PATIENT_FILE


class PatientManager:

    def __init__(self):
        self.reload()

    #####################################################

    def reload(self):
        db.reload()
        self.df = db.patients

    #####################################################

    def get_all_patients(self):

        self.reload()

        return self.df.to_dict(orient="records")

    #####################################################

    def get_patient_by_id(self, patient_id):

        self.reload()

        patient = self.df[
            self.df["PATIENT ID"] == patient_id
        ]

        if patient.empty:
            return None

        return patient.iloc[0].to_dict()

    #####################################################

    def get_patient_by_name(self, patient_name):

        self.reload()

        patient = self.df[
            self.df["PATIENT NAME"].str.lower() == patient_name.lower()
        ]

        if patient.empty:
            return None

        return patient.iloc[0].to_dict()

    #####################################################

    def get_patients_by_gender(self, gender):

        self.reload()

        patient = self.df[
            self.df["GENDER"].str.lower() == gender.lower()
        ]

        return patient.to_dict(orient="records")

    #####################################################

    def generate_patient_id(self):

        self.reload()

        if self.df.empty:
            return "PAT-001"

        ids = []

        for pid in self.df["PATIENT ID"]:

            try:
                ids.append(
                    int(str(pid).replace("PAT-", ""))
                )
            except:
                pass

        if len(ids) == 0:
            return "PAT-001"

        new_id = max(ids) + 1

        return f"PAT-{new_id:03d}"

    #####################################################

    def register_patient(self, patient):

        self.reload()

        patient["PATIENT ID"] = self.generate_patient_id()

        patient["SL NO"] = len(self.df) + 1

        self.df = pd.concat(
            [self.df, pd.DataFrame([patient])],
            ignore_index=True
        )

        self.df.to_excel(
            PATIENT_FILE,
            index=False
        )

        return patient["PATIENT ID"]

    #####################################################

    def update_patient(self, patient_id, data):

        self.reload()

        index = self.df[
            self.df["PATIENT ID"] == patient_id
        ].index

        if len(index) == 0:
            return False

        row = index[0]

        for key, value in data.items():

            if key in self.df.columns:
                self.df.at[row, key] = value

        self.df.to_excel(
            PATIENT_FILE,
            index=False
        )

        return True

    #####################################################

    def delete_patient(self, patient_id):

        self.reload()

        self.df = self.df[
            self.df["PATIENT ID"] != patient_id
        ]

        self.df.to_excel(
            PATIENT_FILE,
            index=False
        )

        return True