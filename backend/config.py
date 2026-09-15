import os

# =====================================================
# PROJECT PATHS
# =====================================================

# backend/
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Hospital_HMS/
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

# =====================================================
# FOLDERS
# =====================================================

EXCEL_DIR = os.path.join(PROJECT_DIR, "excel")

UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")

LOG_DIR = os.path.join(PROJECT_DIR, "logs")

# =====================================================
# EXCEL FILES
# =====================================================

PATIENT_FILE = os.path.join(EXCEL_DIR, "Patient.xlsx")

DOCTOR_FILE = os.path.join(EXCEL_DIR, "Doctors.xlsx")

DEPARTMENT_FILE = os.path.join(EXCEL_DIR, "Departments.xlsx")

SCHEDULE_FILE = os.path.join(EXCEL_DIR, "Schedule.xlsx")

SERVICE_FILE = os.path.join(EXCEL_DIR, "Services.xlsx")

CONSULTANT_FILE = os.path.join(EXCEL_DIR, "Consultant.xlsx")

CONSULTANT_BILLING_FILE = os.path.join(
    EXCEL_DIR,
    "Consultant Biling.xlsx"
)

SERVICE_BILLING_FILE = os.path.join(
    EXCEL_DIR,
    "Services Billing.xlsx"
)

MAP_FILE = os.path.join(EXCEL_DIR, "Map.xlsx")

FAQ_FILE = os.path.join(
    EXCEL_DIR,
    "Faq.xlsx"
)
APPOINTMENT_FILE = os.path.join(EXCEL_DIR, "Appointments.xlsx")

# =====================================================
# SERVER
# =====================================================

HOST = "127.0.0.1"

PORT = 5000

DEBUG = True
