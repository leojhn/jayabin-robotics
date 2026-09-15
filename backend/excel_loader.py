import os
import pandas as pd

from config import (
    APPOINTMENT_FILE,
    CONSULTANT_BILLING_FILE,
    CONSULTANT_FILE,
    DEPARTMENT_FILE,
    DOCTOR_FILE,
    FAQ_FILE,
    MAP_FILE,
    PATIENT_FILE,
    SCHEDULE_FILE,
    SERVICE_BILLING_FILE,
    SERVICE_FILE,
)


class ExcelLoader:
    """Handles loading and cleaning of Excel database files for HMS."""

    def __init__(self):
        self.reload()

    def load_excel(self, filepath: str) -> pd.DataFrame:
        """Safely loads and cleans an Excel file into a pandas DataFrame."""
        filename = os.path.basename(filepath)

        if not os.path.exists(filepath):
            print(f"[WARNING] {filename} not found.")
            return pd.DataFrame()

        try:
            # Read all columns as object to preserve original values
            df = pd.read_excel(filepath, dtype=object)

            # Clean column headers
            df.columns = df.columns.astype(str).str.strip()

            # Fill missing/NaN values
            df = df.fillna("")

            # Strip whitespace from text values across all object columns
            for column in df.columns:
                df[column] = df[column].apply(
                    lambda val: val.strip() if isinstance(val, str) else val
                )

            print(f"[OK] Loaded {filename}")
            return df

        except Exception as e:
            print(f"[ERROR] Failed to load {filename}: {e}")
            return pd.DataFrame()

    def reload(self):
        """Reloads all HMS database files into memory."""
        print("\n========== LOADING HMS DATABASE ==========\n")

        self.patients = self.load_excel(PATIENT_FILE)
        self.doctors = self.load_excel(DOCTOR_FILE)
        self.departments = self.load_excel(DEPARTMENT_FILE)
        self.schedule = self.load_excel(SCHEDULE_FILE)
        self.services = self.load_excel(SERVICE_FILE)
        self.consultants = self.load_excel(CONSULTANT_FILE)
        self.consultant_billing = self.load_excel(CONSULTANT_BILLING_FILE)
        self.service_billing = self.load_excel(SERVICE_BILLING_FILE)
        self.map = self.load_excel(MAP_FILE)
        self.faq = self.load_excel(FAQ_FILE)
        self.appointments = self.load_excel(APPOINTMENT_FILE)

        print("\n========== DATABASE READY ==========\n")


# Global database instance
db = ExcelLoader()
