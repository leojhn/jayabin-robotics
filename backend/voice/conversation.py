import re
import difflib
from datetime import datetime, date, timedelta
from .hms_client import HMSClient

EN = {
    "intro": "Welcome to Jayabin Hospital.",
    "welcome_back": "Welcome back, {name}. How can I help you today?",
    "new_registered": "Welcome {name}. How can I help you today?",
    "new_patient": "May I have your full name?",
    "robot_intro": "I am Marykutty Junior, the hospital reception and assistance robot developed by Jayabin Robotics and Aviation. I can help with patient check-in, face-based patient identification, new patient registration, collecting information about your problem, suggesting the appropriate hospital department and available doctors, booking appointments, consultant billing, payment guidance, and hospital wayfinding. I can communicate in English and Malayalam and work with the hospital management system. Neo Nano organizes the information you provide and suggests a department; it is not a diagnosis.",
    "reg_name": "May I have your full name?",
    "reg_dob": "What is your date of birth?",
    "reg_dob_confirm": "Is this your correct date of birth?",
    "reg_gender": "",
    "reg_phone": "What is your mobile number?",
    "reg_email": "Would you like to provide your email address?",
    "reg_blood": "",
    "reg_emergency_name": "",
    "reg_emergency_phone": "",
    "reg_address": "May I have your address?",
    "test_suggestion": "Based on the information provided, these tests may be relevant to your visit. Would you like to add or continue with these suggested tests? Or would you like to consult the doctor?",
    "invalid": "I did not get a valid answer for that question. {question}",
    "main": "What happens now?",
    "onset": "When did this problem start?",
    "characteristics": "How does it feel?",
    "related": "Have you noticed any other difficulties along with it?",
    "severity": "How severe is it right now?",
    "trend": "Is the problem getting better, getting worse, or staying the same?",
    "prior_occurrence": "Has this happened to you before?",
    "aggravating_relief": "Is there anything that makes it better or worse?",
    "med_allergy": "Have you taken any medicine or treatment for this problem?",
    "duration": "How long have you been experiencing it?",
    "family": "Do you have any previous medical condition or anything related to this problem?",
    "medications": "Have you taken any medicine or treatment for this problem?",
    "allergies": "Do you have any allergies to medicines or anything else?",
    "last_doctor": "Have you consulted a doctor about this problem before?",
    "analyzing": "Thank you. I will now review the information and suggest the most suitable department and doctors.",
    "suggested": "Based on the information you provided, the priority department is {department}. Can we continue your registration with this priority department?",
    "departments": "Which department would you like for the appointment? Please tell me the department name.",
    "department_request": "Which department would you like for the appointment? Please tell me the department name.",
    "doctors": "The available doctors in {department} are: {items}. Which doctor would you like?",
    "doctor_one": "The available doctor in {department} is {doctor}. Would you like this doctor?",
    "date": "What date would you like for the appointment?",
    "time": "What time would you like for the appointment?",
    "confirm": "Would you like to confirm this appointment with {doctor}?",
    "booked": "Your appointment with {doctor} in {department} on {date} at {time} is confirmed.",
    "billing": "Your consultation and selected tests have been added to your bill. Would you like to continue to payment?",
    "payment": "How would you like to pay: UPI, card, or cash?",
    "upi": "UPI selected. Please complete the payment manually on the payment screen.",
    "card": "Card selected. Please complete the payment manually on the secure payment screen.",
    "cash": "If cash, please go to the reception payment area.",
    "wayfinding": "{completion}",
    "thankyou": "Thank you. Please proceed to the department. Have a good day.",
    "error": "I am sorry, I could not complete that step. You can use the touchscreen or try again.",
}

ML = {
    "intro": "ജയാബിൻ ഹോസ്പിറ്റലിലേക്ക് സ്വാഗതം.",
    "welcome_back": "വീണ്ടും സ്വാഗതം, {name}. ഇന്ന് എങ്ങനെ സഹായിക്കാം?",
    "new_registered": "വീണ്ടും സ്വാഗതം, {name}. ഇന്ന് എങ്ങനെ സഹായിക്കാം?",
    "new_patient": "നിങ്ങളുടെ പൂർണ്ണ പേര് പറയാമോ?",
    "robot_intro": "ഞാൻ ജയാബിൻ റോബോട്ടിക്സ് ആൻഡ് ഏവിയേഷൻ വികസിപ്പിച്ച മേരിക്കുട്ടി ജൂനിയർ എന്ന ആശുപത്രി റിസപ്ഷൻ ആൻഡ് അസിസ്റ്റൻസ് റോബോട്ടാണ്. രോഗിയുടെ ചെക്ക്-ഇൻ, മുഖം തിരിച്ചറിയൽ, പുതിയ രോഗിയുടെ രജിസ്ട്രേഷൻ, രോഗി പറയുന്ന പ്രശ്നത്തെക്കുറിച്ചുള്ള വിവരശേഖരണം, അനുയോജ്യമായ ആശുപത്രി വിഭാഗവും ലഭ്യമായ ഡോക്ടർമാരെയും നിർദ്ദേശിക്കൽ, അപ്പോയിന്റ്മെന്റ് ബുക്കിംഗ്, കൺസൾട്ടന്റ് ബില്ലിംഗ്, പേയ്മെന്റ് മാർഗനിർദ്ദേശം, ആശുപത്രിയിലെ വഴി കാണിക്കൽ എന്നിവയിൽ ഞാൻ സഹായിക്കും. ഇംഗ്ലീഷിലും മലയാളത്തിലും സംസാരിക്കാനും ആശുപത്രി മാനേജ്മെന്റ് സിസ്റ്റവുമായി പ്രവർത്തിക്കാനും എനിക്ക് കഴിയും. നിയോ നാനോ നിങ്ങൾ നൽകുന്ന വിവരങ്ങൾ ക്രമീകരിച്ച് ഒരു വിഭാഗം നിർദ്ദേശിക്കുന്നു; ഇത് രോഗനിർണ്ണയം അല്ല.",
    "reg_name": "നിങ്ങളുടെ പൂർണ്ണ പേര് പറയാമോ?",
    "reg_dob": "നിങ്ങളുടെ ജനന തീയതി പറയാമോ?",
    "reg_dob_confirm": "നിങ്ങൾ പറഞ്ഞ ജനന തീയതി ശരിയാണോ പരിശോധിക്കുക?",
    "reg_gender": "",
    "reg_phone": "നിങ്ങളുടെ മൊബൈൽ നമ്പർ പറയാമോ?",
    "reg_email": "നിങ്ങളുടെ ഇമെയിൽ വിലാസം നൽകാമോ?",
    "reg_blood": "",
    "reg_emergency_name": "",
    "reg_emergency_phone": "",
    "reg_address": "നിങ്ങളുടെ വിലാസം പറയാമോ?",
    "test_suggestion": "നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ, ഈ പരിശോധനകൾ ചെയ്തു ഡോക്ടറെ കണ്ടാൽ അത് കൂടുതൽ എളുപ്പം ആകും. നിർദ്ദേശിച്ച പരിശോധനകൾ കൂടി ചേർത്ത് തുടരണമോ, അതോ ആദ്യം ഡോക്ടറെ കാണണമോ?",
    "invalid": "ഈ ചോദ്യത്തിന് ശരിയായ ഉത്തരം ലഭിച്ചില്ല. {question}",
    "main": "ഇപ്പോൾ നിങ്ങളെ എന്താണ് ബുദ്ധിമുട്ടിക്കുന്നത്?",
    "onset": "ഈ പ്രശ്നം എപ്പോഴാണ് തുടങ്ങിയത്?",
    "characteristics": "ഇത് എങ്ങനെയാണ് അനുഭവപ്പെടുന്നത്?",
    "related": "ഇതിനോടൊപ്പം മറ്റെന്തെങ്കിലും ബുദ്ധിമുട്ടുകൾ ശ്രദ്ധിച്ചിട്ടുണ്ടോ?",
    "severity": "ഇപ്പോൾ ഈ പ്രശ്നം എത്രത്തോളം ബുദ്ധിമുട്ടാണ്?",
    "trend": "ഈ പ്രശ്നം കുറയുകയാണോ, കൂടുകയാണോ, അതോ മാറ്റമില്ലാതെ തുടരുകയാണോ?",
    "prior_occurrence": "ഇതുപോലൊരു പ്രശ്നം മുമ്പും ഉണ്ടായിട്ടുണ്ടോ?",
    "aggravating_relief": "ഈ പ്രശ്നം കുറയാനോ കൂടാനോ കാരണമാകുന്ന മറ്റ് എന്തെങ്കിലും ഉണ്ടോ?",
    "med_allergy": "ഈ പ്രശ്നത്തിനായി എന്തെങ്കിലും മരുന്നോ ചികിത്സയോ എടുത്തിട്ടുണ്ടോ?",
    "duration": "എത്ര കാലമായി നിങ്ങൾക്ക് ഈ പ്രശ്നം അനുഭവപ്പെടുന്നു?",
    "family": "നിങ്ങൾക്ക് മുമ്പ് ഉണ്ടായിരുന്ന ഏതെങ്കിലും രോഗാവസ്ഥയോ, ഈ പ്രശ്നവുമായി ബന്ധപ്പെട്ട ആരോഗ്യപ്രശ്നങ്ങളോ ഉണ്ടോ?",
    "medications": "ഈ പ്രശ്നത്തിനായി എന്തെങ്കിലും മരുന്നോ ചികിത്സയോ എടുത്തിട്ടുണ്ടോ?",
    "allergies": "മരുന്നുകളോട് അലർജി ഉണ്ടോ?",
    "last_doctor": "ഈ പ്രശ്നത്തെക്കുറിച്ച് മുമ്പ് ഏതെങ്കിലും ഡോക്ടറെ കണ്ടിട്ടുണ്ടോ?",
    "analyzing": "നന്ദി. വിവരങ്ങൾ പരിശോധിച്ച് അനുയോജ്യമായ വിഭാഗവും ഡോക്ടർമാരെയും നിർദ്ദേശിക്കാം.",
    "suggested": "നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ മുൻഗണന നൽകുന്ന വിഭാഗം {department} ആണ്. ഈ മുൻഗണനാ വിഭാഗത്തിൽ രജിസ്ട്രേഷൻ തുടരട്ടേ?",
    "departments": "അപ്പോയിന്റ്മെന്റിനായി ഏത് വിഭാഗമാണ് വേണ്ടത്? ദയവായി വിഭാഗത്തിന്റെ പേര് പറയൂ.",
    "department_request": "അപ്പോയിന്റ്മെന്റിനായി ഏത് വിഭാഗമാണ് വേണ്ടത്? ദയവായി വിഭാഗത്തിന്റെ പേര് പറയൂ.",
    "doctors": "{department} വിഭാഗത്തിലെ ലഭ്യമായ ഡോക്ടർമാർ: {items}. ഏത് ഡോക്ടറെയാണ് തിരഞ്ഞെടുക്കുന്നത്?",
    "doctor_one": "{department} വിഭാഗത്തിൽ ലഭ്യമായ ഡോക്ടർ {doctor} ആണ്. ഈ ഡോക്ടറെ തിരഞ്ഞെടുക്കണോ?",
    "date": "അപ്പോയിന്റ്മെന്റിനുള്ള തീയതി പറയൂ.",
    "time": "അപ്പോയിന്റ്മെന്റിന് ഏത് സമയമാണ് നിങ്ങൾക്ക് സൗകര്യം?",
    "confirm": "{doctor} ഡോക്ടറുമായുള്ള അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിക്കട്ടേ?",
    "booked": "{department} വിഭാഗത്തിലെ {doctor}നുള്ള {date} തീയതി {time} സമയത്തെ അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിച്ചു.",
    "billing": "നിങ്ങളുടെ കൺസൾട്ടേഷൻ ഫീസും തിരഞ്ഞെടുത്ത പരിശോധനകളുടെ ചാർജും ബില്ലിൽ ഉൾപ്പെടുത്തിയിട്ടുണ്ട്. പേയ്മെന്റിലേക്ക് തുടരട്ടേ?",
    "payment": "എങ്ങനെ പേയ്മെന്റ് നടത്തണം: UPI, കാർഡ്, അല്ലെങ്കിൽ ക്യാഷ്?",
    "upi": "UPI തിരഞ്ഞെടുത്തു. സ്ക്രീനിൽ പേയ്മെന്റ് മാനുവലായി പൂർത്തിയാക്കൂ.",
    "card": "കാർഡ് തിരഞ്ഞെടുത്തു. സുരക്ഷിതമായ പേയ്മെന്റ് സ്ക്രീനിൽ പേയ്മെന്റ് മാനുവലായി പൂർത്തിയാക്കൂ.",
    "cash": "ക്യാഷ് പേയ്മെന്റിനായി ദയവായി റിസപ്ഷൻ പേയ്മെന്റ് കൗണ്ടറിലേക്ക് പോകൂ.",
    "wayfinding": "{completion}",
    "thankyou": "നന്ദി. ദയവായി ബന്ധപ്പെട്ട വിഭാഗത്തിലേക്ക് പോകൂ. നല്ല ദിവസം ആശംസിക്കുന്നു.",
    "error": "ക്ഷമിക്കണം, ഈ ഘട്ടം പൂർത്തിയാക്കാൻ കഴിഞ്ഞില്ല. ടച്ച്സ്ക്രീൻ ഉപയോഗിക്കുകയോ വീണ്ടും ശ്രമിക്കുകയോ ചെയ്യൂ.",
}

REG_STATES = ["REG_NAME", "REG_PHONE", "REG_DOB", "REG_DOB_CONFIRM", "REG_EMAIL", "REG_ADDRESS"]
SYMPTOM_STATES = ["symptoms", "onset", "duration", "prior_occurrence", "characteristics", "severity", "trend", "related_symptoms", "aggravating_relief", "medications", "allergies", "last_doctor_visit", "previous_condition"]
SYMPTOM_PROMPT = {
    "symptoms": "main", "onset": "onset", "duration": "duration",
    "prior_occurrence": "prior_occurrence", "characteristics": "characteristics",
    "severity": "severity", "trend": "trend", "related_symptoms": "related",
    "aggravating_relief": "aggravating_relief", "medications": "medications",
    "allergies": "allergies", "last_doctor_visit": "last_doctor",
    "previous_condition": "family",
}
BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


def _yes(text):
    x = (text or "").casefold()
    return any(v in x for v in ["yes", "yeah", "yep", "okay", "confirm", "sure", "continue", "this department", "that department", "same department", "അതെ", "ശരി", "തുടരാം", "സ്ഥിരീകരിക്കാം", "ഈ വിഭാഗം"])


def _no(text):
    x = (text or "").casefold()
    return any(v in x for v in ["no", "none", "skip", "not now", "no thanks", "ഇല്ല", "വേണ്ട", "ഒന്നുമില്ല", "ഒഴിവാക്കാം"])


def _other(text):
    x = (text or "").casefold()
    return any(v in x for v in ["other department", "another department", "different department", "മറ്റൊരു വിഭാഗം", "മറ്റൊരു ഡിപ്പാർട്ട്മെന്റ്"])


def _payment_method(text):
    x = (text or "").casefold()
    if any(v in x for v in ["upi", "gpay", "google pay", "phonepe", "paytm"]): return "UPI"
    if any(v in x for v in ["card", "debit", "credit", "കാർഡ്"]): return "Card"
    if any(v in x for v in ["cash", "ക്യാഷ്"]): return "Cash"
    return None


def _thank_you(text):
    x = (text or "").casefold()
    return any(v in x for v in ["thank you", "thanks", "thankyou", "നന്ദി"])


def _norm(text):
    return " ".join(str(text or "").strip().casefold().split())


class ConversationManager:
    def __init__(self):
        self.sessions = {}
        self.hms = HMSClient()

    def create(self, language=None):
        sid = f"voice-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.sessions[sid] = {
            "session_id": sid, "language": language, "state": "WAITING_FACE" if language in ("en-IN", "ml-IN") else "LANGUAGE_SELECTION",
            "language_prompt_count": 0,
            "camera_checkin": False, "camera_mode": None,
            "patient": None, "patient_id": None, "patient_draft": {},
            "symptom_context": {}, "symptom_index": 0,
            "neo_result": None, "recommended_departments": [], "department": None, "doctor": None,
            "doctor_options": [], "department_options": [], "time_options": [],
            "date": None, "time": None, "appointment": None,
            "bill": None, "payment_method": None, "wayfinding": {},
            "initial_concern": "", "face_enrolled": False, "suggested_tests": [], "suggested_doctors": [], "tests_selected": False,
        }
        return self.sessions[sid]

    def get(self, sid):
        return self.sessions.get(sid)

    def say(self, s, key):
        return (ML if s.get("language") == "ml-IN" else EN)[key]

    def _robot_info(self, text):
        x = _norm(text)
        return any(v in x for v in [
            "introduce yourself", "who are you", "what can you do", "what do you do",
            "your features", "your use cases", "tell me about yourself", "what is marykutty",
            "നിങ്ങളെ പരിചയപ്പെടുത്തൂ", "സ്വയം പരിചയപ്പെടുത്തൂ", "നിങ്ങൾ ആരാണ്", "എന്തൊക്കെ ചെയ്യാം",
            "നിങ്ങളുടെ സവിശേഷതകൾ", "ഉപയോഗങ്ങൾ എന്തൊക്കെയാണ്"
        ])

    def _looks_ml(self, text):
        return any("\u0d00" <= c <= "\u0d7f" for c in (text or ""))

    def text(self, sid, user_text):
        s = self.sessions.get(sid)
        if not s:
            raise KeyError("Unknown voice session")
        text = str(user_text or "").strip()
        if not text:
            if s.get("state") == "LANGUAGE_SELECTION":
                return self._result(s, self._language_prompt(s))
            return self._result(s, self.say(s, "error"))

        # Language selection happens before the visit language is known. Do not
        # guess the language from the script here; explicitly understand the
        # spoken language name (English / Malayalam) and lock it for the visit.
        if s.get("state") == "LANGUAGE_SELECTION":
            return self._select_language(s, text)

        if s.get("language") not in ("en-IN", "ml-IN"):
            s["language"] = "ml-IN" if self._looks_ml(text) else "en-IN"

        if self._robot_info(text):
            return self._result(s, self.say(s, "robot_intro"))

        state = s["state"]
        if state == "WAITING_FACE":
            return self._result(s, self.say(s, "intro"))
        if state == "REG_NAME" or state.startswith("REG_"):
            return self._registration(s, text)
        if state == "INITIAL_CONCERN":
            if len(text) < 3:
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "main")))
            s["initial_concern"] = text
            s["symptom_context"]["symptoms"] = text
            s["symptom_index"] = 1
            s["state"] = "SYMPTOM_INTAKE"
            return self._ask_symptom(s, route="neo_nano_symptoms.html")
        if state == "SYMPTOM_INTAKE":
            return self._accept_symptom(s, text)
        if state == "NEO_ANALYZE":
            return self._analyze(s)
        if state == "NEO_RESULT":
            requested = self._match_department(text, s.get("recommended_departments") or [])
            if requested:
                s["department"] = requested; s["state"] = "APPT_DOCTOR"; return self._choose_doctor(s)
            if _other(text): return self._ask_departments(s)
            if _yes(text) and s.get("department"):
                s["state"] = "APPT_DOCTOR"; return self._choose_doctor(s)
            return self._ask_departments(s)
        if state == "APPT_DEPARTMENT":
            return self._select_department(s, text)
        if state == "APPT_DOCTOR":
            return self._select_doctor(s, text)
        if state == "TEST_SUGGESTION":
            if _yes(text):
                s["tests_selected"] = True; s["state"] = "APPT_DATE"; return self._result(s, self.say(s, "date"), "appointments.html")
            if _no(text) or any(v in _norm(text) for v in ["consult doctor", "doctor first", "ഡോക്ടറെ കാണാം", "ഡോക്ടറെ ആദ്യം"]):
                s["tests_selected"] = False; s["state"] = "APPT_DATE"; return self._result(s, self.say(s, "date"), "appointments.html")
            return self._result(s, self.say(s, "test_suggestion"))
        if state == "APPT_DATE":
            parsed = self._parse_date(text)
            if not parsed or parsed < date.today():
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "date")))
            s["date"] = parsed.isoformat()
            s["state"] = "APPT_TIME"
            return self._ask_time(s)
        if state == "APPT_TIME":
            return self._select_time(s, text)
        if state == "APPT_CONFIRM":
            if _yes(text): return self._book(s)
            return self._result(s, self.say(s, "confirm").format(department=s["department"], doctor=s["doctor"], date=s["date"], time=s["time"]))
        if state == "DASHBOARD":
            return self._load_bill(s)
        if state == "BILLING" or state == "PAYMENT":
            method = _payment_method(text)
            if not method:
                return self._result(s, self.say(s, "payment"))
            s["payment_method"] = method
            s["state"] = "PAYMENT"
            prompt = self.say(s, method.lower())
            result = self._result(s, prompt, "consultant_bill.html")
            result["open_payment"] = method
            return result
        if state in {"WAYFINDING", "PRINTING"}:
            if state == "PRINTING":
                s["state"] = "WAYFINDING"
            if _thank_you(text):
                s["state"] = "END"
                return self._result(s, self.say(s, "thankyou"), "thankyou.html")
            return self._result(s, self.say(s, "wayfinding").format(department=s["department"], directions=self._directions(s)))
        if state == "END":
            return self._result(s, self.say(s, "thankyou"), "thankyou.html")
        return self._result(s, self.say(s, "error"))

    def _registration_prompt(self, s):
        mapping = {
            "REG_NAME": "reg_name", "REG_PHONE": "reg_phone", "REG_DOB": "reg_dob",
            "REG_DOB_CONFIRM": "reg_dob_confirm", "REG_EMAIL": "reg_email", "REG_ADDRESS": "reg_address",
        }
        return self.say(s, mapping[s["state"]])

    def _clean(self, text, prefixes):
        value = str(text or "").strip()
        low = value.casefold()
        for p in prefixes:
            if low.startswith(p.casefold()):
                return value[len(p):].strip(" .,:;-")
        return value

    def _spoken_name(self, text):
        return self._clean(text, ["my name is ", "i am ", "i'm ", "this is ", "എന്റെ പേര് ", "ഞാൻ "])

    def _spoken_phone(self, text):
        digits = re.sub(r"\D", "", text)
        return digits[-15:] if len(digits) > 15 else digits

    def _language_prompt(self, s):
        # First greeting is intentionally short. If the patient does not
        # respond, the next prompt explicitly asks for the language.
        count = int(s.get("language_prompt_count", 0) or 0)
        if count == 0:
            s["language_prompt_count"] = 1
            return "Welcome to Jayabin Hospital."
        return "Welcome to Jayabin Hospital. Please select your language."

    def _select_language(self, s, text):
        x = _norm(text)
        if any(v in x for v in ["malayalam", "മലയാളം", "malayalee", "മലയാളി"]):
            s["language"] = "ml-IN"
            s["state"] = "WAITING_FACE"
            return self._result(s, "മലയാളം തിരഞ്ഞെടുത്തു. തുടരാം.", "checkin.html")
        if any(v in x for v in ["english", "inglish", "ഇംഗ്ലീഷ്"]):
            s["language"] = "en-IN"
            s["state"] = "WAITING_FACE"
            return self._result(s, "English selected. Let's continue.", "checkin.html")
        # If the answer was not a language name, repeat the language prompt.
        return self._result(s, self._language_prompt(s))

    def _spoken_date(self, text):
        x = str(text or "").strip()
        # Common STT output: 15 08 2000 / 15-08-2000 / 15/08/2000.
        m = re.search(r"\b(\d{1,2})\s*[/-]\s*(\d{1,2})\s*[/-]\s*(\d{2,4})\b", x)
        if not m:
            m = re.search(r"\b(\d{1,2})\s+(\d{1,2})\s+(\d{4})\b", x)
        if m:
            d, mn, y = map(int, m.groups()); y += 2000 if y < 100 else 0
            try: return date(y, mn, d).isoformat()
            except ValueError: return None

        # Handle spoken-number dates before fuzzy parsing so phrases such as
        # "twenty fifth March two thousand" are not misread by dateutil.
        number_words = {
            "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,
            "ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
            "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,"thirty":30,
            "forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90,
            "first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,
            "eighth":8,"ninth":9,"tenth":10,"eleventh":11,"twelfth":12,"thirteenth":13,
            "fourteenth":14,"fifteenth":15,"sixteenth":16,"seventeenth":17,"eighteenth":18,
            "nineteenth":19,"twentieth":20,"thirtieth":30,
        }
        months = {m.lower():i for i,m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"],1)}
        tokens = re.sub(r"[,.-]", " ", x.casefold()).split()
        month_i = next((months[t] for t in tokens if t in months), None)
        if month_i:
            mi = next(i for i,t in enumerate(tokens) if t in months)
            before = tokens[max(0,mi-3):mi]
            after = tokens[mi+1:mi+6]
            day = None; year = None
            day_tokens = before + after
            for t in day_tokens:
                if t.isdigit() and 1 <= int(t) <= 31 and day is None: day = int(t)
                elif t in number_words and day is None: day = number_words[t]
            for a,b in zip(day_tokens, day_tokens[1:]):
                if a in ("twenty","thirty","forty","fifty") and b in number_words:
                    candidate = number_words[a] + number_words[b]
                    if candidate <= 31:
                        day = candidate
                        break
            # Handle spoken years like "two thousand" / "two thousand and five".
            for i,t in enumerate(after):
                if t == "thousand" and i > 0 and after[i-1] in number_words:
                    year = number_words[after[i-1]] * 1000
                    if i+1 < len(after) and after[i+1] == "and":
                        if i+2 < len(after) and after[i+2] in number_words:
                            year += number_words[after[i+2]]
                    elif i+1 < len(after) and after[i+1] in number_words:
                        year += number_words[after[i+1]]
                    break
            if day and year:
                try: return date(year, month_i, day).isoformat()
                except ValueError: return None

        # Finally handle normal spoken dates such as "25 March 2000" and
        # "March 25 2000" using a locale-independent day-first parser.
        try:
            from dateutil import parser
            return parser.parse(x, dayfirst=True, fuzzy=True).date().isoformat()
        except Exception:
            return None

    def _registration(self, s, text):
        key = s["state"]
        skipped = _no(text) or _norm(text) in {"skip", "none", "not applicable", "unknown", "അറിയില്ല", "ഒഴിവാക്കാം"}
        if key == "REG_NAME":
            value = self._spoken_name(text)
            if len(value) < 2 or not re.search(r"[A-Za-z\u0d00-\u0d7f]", value):
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_name")))
            s["patient_draft"]["PATIENT NAME"] = value; s["state"] = "REG_PHONE"
        elif key == "REG_PHONE":
            value = self._spoken_phone(text)
            if len(value) < 10 or len(value) > 15:
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_phone")))
            s["patient_draft"]["PHONE"] = value; s["state"] = "REG_DOB"
        elif key == "REG_DOB":
            value = self._spoken_date(text)
            if not value or date.fromisoformat(value) > date.today():
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_dob")))
            dob = date.fromisoformat(value); today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 0 or age > 130:
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_dob")))
            s["patient_draft"]["DATE OF BIRTH"] = value; s["patient_draft"]["AGE"] = age
            s["state"] = "REG_DOB_CONFIRM"
            return self._result(s, self.say(s, "reg_dob_confirm"))
        elif key == "REG_DOB_CONFIRM":
            if _yes(text): s["state"] = "REG_EMAIL"
            elif _no(text): s["state"] = "REG_DOB"; return self._result(s, self.say(s, "reg_dob"))
            else: return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_dob_confirm")))
        elif key == "REG_EMAIL":
            value = "" if skipped else self._clean(text, ["my email is ", "email is ", "എന്റെ ഇമെയിൽ "])
            if value and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value):
                return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_email")))
            s["patient_draft"]["EMAIL"] = value; s["state"] = "REG_ADDRESS"
        elif key == "REG_ADDRESS":
            if len(text.strip()) < 5: return self._result(s, self.say(s, "invalid").format(question=self.say(s, "reg_address")))
            s["patient_draft"]["ADDRESS"] = text.strip()
            try:
                result = self.hms.register_patient(dict(s["patient_draft"]))
                pid = result.get("patient_id")
                if not pid: raise RuntimeError(result.get("message", "Registration failed"))
                s["patient_id"] = pid; s["patient"] = self.hms.patient(pid)
                try:
                    from .face_service import enroll_from_camera
                    enroll_from_camera(pid); s["face_enrolled"] = True
                except Exception: s["face_enrolled"] = False
                s["state"] = "INITIAL_CONCERN"; s["symptom_index"] = 0
                name = s["patient"].get("PATIENT NAME") if s["patient"] else s["patient_draft"].get("PATIENT NAME", "there")
                return self._result(s, self.say(s, "new_registered").format(name=name), "neo_nano_symptoms.html")
            except Exception: return self._result(s, self.say(s, "error"))
        return self._result(s, self._registration_prompt(s), "new_patient.html")

    def _accept_symptom(self, s, text):
        key = SYMPTOM_STATES[s["symptom_index"]]
        value = text.strip(); x = _norm(value); valid = bool(value)
        if key == "onset": valid = bool(re.search(r"\d|today|yesterday|ago|since|week|month|day|ഇന്ന്|ഇന്നലെ|ദിവസം|ആഴ്ച|മാസ", x))
        elif key == "duration": valid = len(value) >= 2
        elif key == "severity": valid = bool(re.search(r"\d|mild|moderate|severe|low|high|light|medium|കുറവ്|കൂടുതൽ|തീവ്ര", x))
        elif key == "trend": valid = any(v in x for v in ["better","worse","same","improving","getting better","getting worse","മാറുന്നില്ല","കുറയ","കൂട","മാറ്റമില്ല"])
        elif key in {"prior_occurrence", "last_doctor_visit"}: valid = _yes(value) or _no(value) or len(value) >= 2
        if not valid: return self._result(s, self.say(s, "invalid").format(question=self.say(s, SYMPTOM_PROMPT[key])))
        if key in {"prior_occurrence","related_symptoms","medications","allergies","last_doctor_visit","previous_condition"} and _no(value): value = "None reported"
        s["symptom_context"][key] = value
        if key == "symptoms": s["initial_concern"] = value
        s["symptom_index"] += 1
        if s["symptom_index"] >= len(SYMPTOM_STATES): s["state"] = "NEO_ANALYZE"; return self._analyze(s)
        return self._ask_symptom(s)

    def _ask_symptom(self, s, route=None):
        key = SYMPTOM_STATES[s["symptom_index"]]
        return self._result(s, self.say(s, SYMPTOM_PROMPT[key]), route)

    def _analyze(self, s):
        try:
            ctx = dict(s["symptom_context"])
            patient = s.get("patient") or {}
            ctx["age"] = patient.get("AGE") or patient.get("Age") or ""
            result = self.hms.neo_analyze(ctx.get("symptoms", ""), ctx)
            s["neo_result"] = result
            recommendations = [
                str(v).strip()
                for v in (result.get("recommended_departments") or [])
                if str(v).strip()
            ][:3]
            if not recommendations:
                recommendations = [str(result.get("department") or "General Medicine").strip()]
            s["recommended_departments"] = recommendations
            s["department"] = recommendations[0]
            s["suggested_tests"] = result.get("tests") or []
            doctor_names = []
            for dep in recommendations:
                try: doctor_names.extend([d.get("name", "") for d in self.hms.doctors(dep) if d.get("name")])
                except Exception: pass
            s["suggested_doctors"] = doctor_names[:6]
            s["state"] = "NEO_RESULT"
            departments_text = ", ".join(recommendations)
            doctors_text = ", ".join(s["suggested_doctors"]) or "available doctors"
            return self._result(s, self.say(s, "suggested").format(departments=departments_text, doctors=doctors_text, department=s["department"]), "neo_nano_result.html")
        except Exception:
            return self._result(s, self.say(s, "error"))

    def _ask_departments(self, s):
        try:
            deps = self.hms.departments()
            names = [d.get("Department", d.get("department", "")) for d in deps if d.get("Department", d.get("department", ""))]
            s["department_options"] = names
            s["state"] = "APPT_DEPARTMENT"
            # Never read the complete department list. Ask the patient to say
            # the department they want; the next response is matched to HMS.
            return self._result(
                s,
                self.say(s, "department_request"),
                "appointments.html"
            )
        except Exception:
            return self._result(s, self.say(s, "error"))

    def _select_department(self, s, text):
        options = s.get("department_options") or self._get_departments()
        match = self._match_department(text, options)
        if not match:
            return self._ask_departments(s)
        s["department"] = match
        s["state"] = "APPT_DOCTOR"
        return self._choose_doctor(s)

    def _get_departments(self):
        try:
            return [d.get("Department", d.get("department", "")) for d in self.hms.departments()]
        except Exception:
            return []

    def _choose_doctor(self, s):
        try:
            docs = self.hms.doctors(s["department"])
            names = [d.get("Doctor Name", d.get("name", "")) for d in docs if d.get("Doctor Name", d.get("name", ""))]
            s["doctor_options"] = names
            if not names:
                return self._result(s, self.say(s, "error"))
            if len(names) == 1:
                s["state"] = "APPT_DOCTOR"
                return self._result(s, self.say(s, "doctor_one").format(department=s["department"], doctor=names[0]), "appointments.html")
            return self._result(s, self.say(s, "doctors").format(department=s["department"], items=", ".join(names)), "appointments.html")
        except Exception:
            return self._result(s, self.say(s, "error"))

    def _select_doctor(self, s, text):
        options = s.get("doctor_options") or []
        if len(options) == 1 and (_yes(text) or self._matches_option(text, options)):
            match = options[0]
        else:
            match = self._match_option(text, options)
        if not match:
            return self._choose_doctor(s)
        s["doctor"] = match
        if s.get("suggested_tests"):
            s["state"] = "TEST_SUGGESTION"; return self._result(s, self.say(s, "test_suggestion"))
        s["state"] = "APPT_DATE"; return self._result(s, self.say(s, "date"), "appointments.html")

    def _ask_time(self, s):
        options = self._available_times(s["doctor"], s["date"])
        s["time_options"] = options
        # Do not read or display the available times. The patient simply says the time.
        # Backend validation still checks the spoken time against the doctor schedule.
        return self._result(s, self.say(s, "time"), "appointments.html")

    def _available_times(self, doctor, appointment_date):
        try:
            rows = self.hms.schedule(doctor)
            weekday = date.fromisoformat(appointment_date).strftime("%A").casefold()
            values = []
            for row in rows:
                day = str(row.get("Day", "")).strip().casefold()
                if day and day != weekday and weekday[:3] not in day and day[:3] not in weekday:
                    continue
                raw = str(row.get("OPD Time", row.get("Time", ""))).strip()
                for part in re.split(r"[,;]", raw):
                    part = part.strip().replace("–", "-")
                    if "-" in part:
                        a,b = [x.strip() for x in part.split("-",1)]
                        start=self._normalize_time(a); end=self._normalize_time(b)
                        if start and end:
                            sh,sm=map(int,start.split(":")); eh,em=map(int,end.split(":"))
                            cur=sh*60+sm; finish=eh*60+em
                            if finish < cur: finish += 24*60
                            while cur <= finish:
                                h=(cur//60)%24; m=cur%60; values.append(f"{h:02d}:{m:02d}"); cur+=15
                    else:
                        t=self._normalize_time(part)
                        if t: values.append(t)
            return list(dict.fromkeys(values))
        except Exception:
            return []

    def _select_time(self, s, text):
        options = s.get("time_options") or []
        spoken = self._normalize_time(text)
        if options:
            normalized = {self._normalize_time(v): v for v in options}
            if spoken not in normalized:
                match = self._match_option(text, options)
                if not match:
                    return self._ask_time(s)
                chosen = match
            else:
                chosen = normalized[spoken]
        else:
            chosen = spoken
        if not chosen:
            return self._ask_time(s)
        s["time"] = chosen
        s["state"] = "APPT_CONFIRM"
        return self._result(s, self.say(s, "confirm").format(department=s["department"], doctor=s["doctor"], date=s["date"], time=chosen))

    def _book(self, s):
        try:
            result = self.hms.book(s["patient_id"], s["department"], s["doctor"], s["date"], s["time"])
            if not result.get("success"):
                return self._result(s, result.get("message", self.say(s, "error")))
            s["appointment"] = result.get("appointment")
            s["state"] = "DASHBOARD"
            return self._result(s, self.say(s, "booked").format(department=s["department"], doctor=s["doctor"], date=s["date"], time=s["time"]), "dashboard.html")
        except Exception:
            return self._result(s, self.say(s, "error"))

    def _load_bill(self, s):
        try:
            s["bill"] = self.hms.consultant_bill(s["patient_id"])
            s["state"] = "PAYMENT"
            amount = self._bill_amount(s)
            return self._result(s, self.say(s, "billing").format(amount=amount), "consultant_bill.html")
        except Exception:
            return self._result(s, self.say(s, "error"))

    def _bill_amount(self, s):
        b = s.get("bill") or {}
        for key in ("Total", "total", "Amount", "amount"):
            try: return float(b.get(key, 0))
            except Exception: pass
        return 0

    def _wayfinding(self, s, speech="", route="wayfinding.html"):
        try:
            s["wayfinding"] = self.hms.map(s["department"]) or {}
            completion = (f"Your registration and appointment are complete. You selected tests first, so please go to the test area. After the tests, you can go to {s['department']} for consultation." if s.get("tests_selected") and s.get("suggested_tests") else f"Your registration and appointment are complete. Please go to the waiting area of {s['department']} for consultation.")
            if s.get("language") == "ml-IN":
                completion = (f"നിങ്ങളുടെ രജിസ്ട്രേഷനും അപ്പോയിന്റ്മെന്റും പൂർത്തിയായി. നിങ്ങൾ തിരഞ്ഞെടുത്ത പരിശോധന ആദ്യം നടത്തേണ്ടതിനാൽ ദയവായി പരിശോധനാ വിഭാഗത്തിലേക്ക് പോകൂ. പരിശോധന പൂർത്തിയായ ശേഷം {s['department']} വിഭാഗത്തിലേക്ക് കൺസൾട്ടേഷനായി പോകാം." if s.get("tests_selected") and s.get("suggested_tests") else f"നിങ്ങളുടെ രജിസ്ട്രേഷനും അപ്പോയിന്റ്മെന്റും പൂർത്തിയായി. ഇനി {s['department']} വിഭാഗത്തിലെ വെയിറ്റിംഗ് ഏരിയയിലേക്ക് കൺസൾട്ടേഷനായി പോകൂ.")
            direction_text = self.say(s, "wayfinding").format(completion=completion)
            msg = (speech + " " + direction_text).strip() if speech else direction_text
            return self._result(s, msg, route)
        except Exception:
            return self._result(s, speech or self.say(s, "error"), route)

    def _directions(self, s):
        m = s.get("wayfinding") or {}
        return m.get("Location Details") or m.get("Directions") or m.get("direction") or "Please follow the hospital signs."

    def _match_department(self, text, options):
        """Match a spoken department name without exposing the department list."""
        x = _norm(text)
        if not x:
            return None

        # First use the existing exact/substring matcher. This handles natural
        # phrases such as "I want Cardiology" or "Cardiology department".
        match = self._match_option(x, options)
        if match:
            return match

        # Then tolerate small STT variations without changing doctor matching.
        filler = {
            "i", "id", "want", "would", "like", "please", "choose",
            "select", "book", "booking", "appointment", "department",
            "the", "a", "an", "for", "me", "to", "is", "not",
            "this", "that", "another", "one", "give", "go", "with",
            "എനിക്ക്", "വേണം", "വകുപ്പ്", "ഡിപ്പാർട്ട്മെന്റ്", "തിരഞ്ഞെടുക്കണം"
        }
        words = [w for w in re.findall(r"[\w\u0D00-\u0D7F]+", x) if w not in filler]
        spoken = " ".join(words).strip() or x

        normalized = {}
        for option in options or []:
            o = _norm(option)
            if o:
                normalized[o] = option

        if not normalized:
            return None

        # Prefer a close match on the meaningful spoken words.
        close = difflib.get_close_matches(spoken, list(normalized.keys()), n=1, cutoff=0.68)
        if close:
            return normalized[close[0]]

        # Also match an individual meaningful word to a department name.
        for word in words:
            close = difflib.get_close_matches(word, list(normalized.keys()), n=1, cutoff=0.72)
            if close:
                return normalized[close[0]]
        return None

    def _matches_option(self, text, options):
        return bool(self._match_option(text, options))

    def _match_option(self, text, options):
        x = _norm(text)
        for option in options or []:
            o = _norm(option)
            if not o: continue
            if x == o or o in x or x in o:
                return option
        return None

    def _parse_date(self, text):
        x = _norm(text)
        if "today" in x or "ഇന്ന്" in x: return date.today()
        if "tomorrow" in x or "നാളെ" in x: return date.today() + timedelta(days=1)
        m = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", x)
        if m:
            d, mn, y = m.groups(); y = int(y) if y else date.today().year; y += 2000 if y < 100 else 0
            try: return date(int(y), int(mn), int(d))
            except Exception: return None
        try:
            from dateutil import parser
            return parser.parse(x, dayfirst=True, fuzzy=True).date()
        except Exception:
            return None

    def _normalize_time(self, text):
        x = str(text or "").upper().strip()
        m = re.search(r"(\d{1,2})(?::(\d{1,2}))?\s*(AM|PM)?", x)
        if not m: return None
        h = int(m.group(1)); mi = int(m.group(2) or 0); ap = m.group(3)
        if ap == "PM" and h < 12: h += 12
        if ap == "AM" and h == 12: h = 0
        if not ap and h < 8: h += 12
        if h > 23 or mi > 59: return None
        return f"{h:02d}:{mi:02d}"

    def _autofill(self, s):
        out = {}
        merged = dict(s.get("patient") or {})
        merged.update(s.get("patient_draft") or {})
        mapping = {
            "PATIENT ID":"patientId", "PATIENT NAME":"patientName", "DATE OF BIRTH":"patientDob", "AGE":"patientAge",
            "GENDER":"patientGender", "PHONE":"patientPhone", "EMAIL":"patientEmail", "BLOOD GROUP":"bloodGroup",
            "EMERGENCY CONTACT NAME":"emergencyName", "EMERGENCY CONTACT":"emergencyPhone", "ADDRESS":"patientAddress",
        }
        for key, eid in mapping.items():
            if merged.get(key) not in (None, ""): out[eid] = merged[key]
        ctx = s.get("symptom_context") or {}
        symptom_map = {
            "symptoms":"symptoms", "onset":"onset", "duration":"duration", "prior_occurrence":"prior_occurrence",
            "characteristics":"characteristics", "severity":"severity", "trend":"trend", "related_symptoms":"related_symptoms",
            "aggravating_relief":"aggravating_relief", "medications":"medications", "allergies":"allergies",
            "last_doctor_visit":"last_doctor_visit", "previous_condition":"previous_condition"
        }
        for key,eid in symptom_map.items():
            if ctx.get(key) not in (None, ""): out[eid] = ctx[key]
        if s.get("department"): out["department"] = s["department"]
        if s.get("doctor"): out["doctor"] = s["doctor"]
        if s.get("date"): out["appointmentDate"] = s["date"]
        if s.get("time"): out["opdTime"] = s["time"]
        if s.get("appointment"):
            ap=s["appointment"]
            for k,eid in {"Appointment ID":"appointmentId","Token":"tokenNo","Date":"appointmentDate","Time":"appointmentTime","Doctor":"doctor","Department":"department"}.items():
                if ap.get(k) not in (None, ""): out[eid]=ap[k]
        bill=s.get("bill") or {}
        for k,eid in {"Consultant":"doctor","Consultation Fee":"consultantAmount","Total":"consultationTotal","Payment Status":"consultantStatus","Appointment ID":"appointmentId","Token":"tokenNo"}.items():
            if bill.get(k) not in (None, ""): out[eid]=bill[k]
        # Appointment/voice selections are authoritative; billing data must
        # never replace the department, date, or time selected for this visit.
        if not s.get("department") and bill.get("Department") not in (None, ""):
            out["department"] = bill["Department"]
        if not s.get("date") and bill.get("Date") not in (None, ""):
            out["appointmentDate"] = bill["Date"]
        if not s.get("time") and bill.get("Time") not in (None, ""):
            out["appointmentTime"] = bill["Time"]
        if bill.get("Total") not in (None, ""): out["grandTotal"] = bill["Total"]
        wf=s.get("wayfinding") or {}
        for k,eid in {"Department":"department","Floor":"floor","Room":"room","Room No.":"room","Room Number":"room","Directions":"direction","Location Details":"direction","direction":"direction"}.items():
            if wf.get(k) not in (None, ""): out[eid]=wf[k]
        if wf.get("More Details") not in (None, ""):
            out["mapImage"] = wf.get("More Details")
        elif wf.get("Map Image") not in (None, ""):
            out["mapImage"] = wf.get("Map Image")
        # Keep the currently selected department authoritative. The Neo Nano
        # recommendation must not overwrite a department chosen by the patient.
        if not s.get("department"):
            neo = s.get("neo_result") or {}
            if neo.get("department"): out["department"] = neo["department"]
        return out

    def _result(self, s, speech, ui_route=None):
        if ui_route: s["ui_route"] = ui_route
        return {
            "session_id": s["session_id"], "speech": speech or "", "language": s.get("language"),
            "state": s.get("state"), "ui_route": s.get("ui_route"), "patient": s.get("patient"),
            "appointment": s.get("appointment"), "department": s.get("department"), "doctor": s.get("doctor"),
            "date": s.get("date"), "time": s.get("time"), "symptom_context": s.get("symptom_context",{}),
            "initial_concern": s.get("initial_concern",""), "neo_result": s.get("neo_result"), "recommended_departments": s.get("recommended_departments", []), "suggested_tests": s.get("suggested_tests", []), "tests_selected": s.get("tests_selected", False), "bill": s.get("bill"),
            "payment_method": s.get("payment_method"), "wayfinding": s.get("wayfinding",{}), "autofill": self._autofill(s)
        }
