# Marykutty Junior – Final Voice + Backend Camera Workflow

1. `index.html` speaks: **Welcome to Jayabin Hospital. Please select your language.** The patient selects English or Malayalam.
2. The system opens `checkin.html`. The C920 camera is owned by the backend only. The browser never opens the camera and never tells the patient to look at it.
3. If the face matches an enrolled Patient ID, HMS loads the patient and Marykutty says: **Welcome back, [Name]. How can I help you today?**
4. If no match is found after the backend recognition window, the new-patient registration page opens. Marykutty asks each registration question one at a time and validates the answer before accepting it. After registration: **Welcome, [Name]. How can I help you today?**
5. The first problem statement is shown in Neo Nano's `What happened?` field. Follow-up questions are spoken/backend-managed. Their answers are validated and stored in the symptom context. After the final follow-up, the recommendation page opens automatically.
6. Neo Nano recommends a department and Marykutty asks whether to use that department or another department. Voice can select the department, doctor, date, and available time. Appointment confirmation books through the HMS API and opens the dashboard automatically.
7. Dashboard shows the appointment confirmation. It then advances automatically to consultant billing.
8. Consultant billing accepts UPI, Card, or Cash by voice or touch. The selected method opens its popup. The actual payment remains manual. Card details/PIN are never collected by the robot.
9. After manual payment confirmation, the wayfinding page opens automatically and displays department, floor, room, directions, and the hospital map image.
10. The patient says **thank you**. Marykutty recognizes that response and opens the final Thank You page.

## Camera
- Default device: `/dev/video2` (Logitech C920)
- Backend only
- Face registry accepts `.jpg`, `.jpeg`, and `.png`
- Existing patient face file example: `backend/face_registry/PAT-051.jpeg`
- New registrations are enrolled against their generated Patient ID after registration.

## Voice
- Gemini Live API
- Gemini Live API
- English and Malayalam
- Put the rotated key in `.env` as `GEMINI_API_KEY=...`

## Start
```bash
source venv/bin/activate
bash setup_face_voice.sh
cd backend
python3 -m app
```
Then open `http://127.0.0.1:5000/`.


APPOINTMENT DATE/TIME UPDATE: The robot asks only "What date would you like?" and "What time would you like?" It does not list dates or times. Backend still validates the spoken date/time against schedule.
WAYFINDING UPDATE: After manual payment completion, the voice bridge explicitly navigates to wayfinding.html. The page loads the department map from Map.xlsx and displays the corresponding image from frontend/images.


## Latest workflow fixes
- Index plays the welcome TTS and retries on first interaction if Chrome blocks autoplay.
- Unknown face check-in routes to the new-patient form; the backend key is `new_patient`.
- Neo Nano voice intake is limited to five natural questions: concern, onset, how it feels/severity, related symptoms, and medicines/allergies.
- Voice autofill never overwrites a field marked as manually edited. Touch can therefore take over a field.
- Appointment flow is Dashboard -> Consultant Billing/Payment -> Receipt printing page -> Wayfinding -> Thank You.
- The receipt page prints to the configured thermal printer and then advances to Wayfinding.
- Service Billing has Return to Menu controls.
