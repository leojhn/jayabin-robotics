# Jayabin Hospital — Marykutty Junior Full Voice + Backend Camera Demo

## Final workflow

1. **Index page:** patient selects English or Malayalam.
2. The selected language is locked for the visit. The system speaks the hospital welcome in that language.
3. The browser immediately opens **`/pages/checkin.html`**.
4. The **backend C920 camera (`/dev/video2`)** checks the patient. The browser never opens the patient camera.
5. If a face matches an HMS patient:
   - Backend retrieves Patient ID and patient record.
   - Robot says: **“Welcome back, [Name]. What happened?”**
   - Neo Nano opens.
6. If a face is present but does not match an enrolled patient:
   - Robot starts **New Patient Registration**.
   - It does **not** ask whether the patient is new or has visited before.
7. Voice fills the active page. Touchscreen/keyboard remains available.
8. A manual edit marks that field as manual and voice will not overwrite it.
9. Neo Nano displays only the patient's first description. Follow-up questions remain in the voice/backend conversation.
10. Department/doctor/date/time are voice-fillable on the appointment page.
11. Appointment → Dashboard → Consulting Billing → Payment → Wayfinding → Thank You.
12. If the patient asks **“Introduce yourself”**, **“What can you do?”**, **“What are your features/use cases?”**, or the Malayalam equivalent, Marykutty Junior answers without changing the workflow state.

## Robot introduction content

Marykutty Junior describes itself as the hospital reception and assistance robot developed by Jayabin Robotics and Aviation. It can explain patient check-in, backend face identification, registration, symptom intake, department/doctor suggestions, appointment booking, billing/payment guidance, wayfinding, multilingual English/Malayalam voice interaction, and HMS integration. It explains that Neo Nano organizes patient-provided information and suggests a department; it is not a diagnosis.

## Setup

```bash
cd ~/Downloads/Hospital_HMS3.3/Hospital_HMS2-updated
source venv/bin/activate
./setup_face_voice.sh
```

Set a newly rotated Gemini key in `.env`:

```text
GEMINI_API_KEY=YOUR_NEW_KEY
```

## Camera verification

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video2 --all
```

The tested Logitech C920 is `/dev/video2`.

## Start

```bash
cd backend
python3 -m app
```

Open:

```text
http://127.0.0.1:5000/
```

Do not run a separate frontend server and do not run a separate browser camera program.

## Camera privacy

The patient camera is backend-only. The frontend does not call `getUserMedia()` for patient identification. The backend owns `/dev/video2` and exposes only recognition status/patient information through Flask.
