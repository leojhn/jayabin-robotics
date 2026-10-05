
import requests
from .config import HMS_API_BASE, VOICE_API_TIMEOUT

class HMSClient:
    def __init__(self, base_url=None):
        self.base = (base_url or HMS_API_BASE).rstrip("/")

    def _get(self, path, **kwargs):
        r = requests.get(self.base + path, timeout=VOICE_API_TIMEOUT, **kwargs)
        r.raise_for_status()
        return r.json()

    def _post(self, path, payload):
        r = requests.post(self.base + path, json=payload, timeout=VOICE_API_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def _put(self, path, payload):
        r = requests.put(self.base + path, json=payload, timeout=VOICE_API_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def patient(self, patient_id):
        return self._get(f"/api/patient/{patient_id}")

    def search_patients(self, q):
        return self._get("/api/patients/search", params={"q": q})

    def register_patient(self, data):
        return self._post("/api/register_patient", data)

    def departments(self):
        return self._get("/api/departments")

    def doctors(self, department):
        return self._get("/api/doctors/{0}".format(requests.utils.quote(department, safe="")))

    def schedule(self, doctor):
        return self._get("/api/schedule/{0}".format(requests.utils.quote(doctor, safe="")))

    def book(self, patient_id, department, doctor, date, time):
        return self._post("/api/book_appointment", {
            "patient_id": patient_id, "department": department,
            "doctor": doctor, "date": date, "time": time
        })

    def consultant_bill(self, patient_id):
        return self._get(f"/api/consultant_bill/{patient_id}")

    def payment_status(self, patient_id, status):
        return self._put("/api/payment_status", {"patient_id": patient_id, "status": status})

    def map(self, department):
        return self._get("/api/map/{0}".format(requests.utils.quote(department, safe="")))

    def neo_analyze(self, symptoms, context):
        return self._post("/api/neo-nano/analyze", {
            "symptoms": symptoms, "symptom_context": context
        })
