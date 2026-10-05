from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
checks = [
    ROOT/'backend/app.py',
    ROOT/'backend/voice/conversation.py',
    ROOT/'backend/voice/face_service.py',
    ROOT/'backend/voice/sarvam_client.py',
    ROOT/'frontend/index.html',
    ROOT/'frontend/menu.html',
    ROOT/'frontend/voice_bridge.js',
    ROOT/'frontend/face_checkin.js',
    ROOT/'frontend/pages/checkin.html',
    ROOT/'frontend/pages/new_patient.html',
    ROOT/'frontend/pages/neo_nano_symptoms.html',
    ROOT/'frontend/pages/neo_nano_result.html',
    ROOT/'frontend/pages/appointments.html',
    ROOT/'frontend/pages/dashboard.html',
    ROOT/'frontend/pages/consultant_bill.html',
    ROOT/'frontend/pages/wayfinding.html',
    ROOT/'frontend/pages/thankyou.html',
]
missing=[str(p.relative_to(ROOT)) for p in checks if not p.exists()]
print('Missing files:', missing or 'none')
app=(ROOT/'backend/app.py').read_text()
voice=(ROOT/'frontend/voice_bridge.js').read_text()
face=(ROOT/'frontend/face_checkin.js').read_text()
print('Root serves index:', 'send_from_directory(frontend_dir, "index.html")' in app)
print('Root frontend asset route:', 'def serve_frontend_asset' in app)
print('Backend camera only:', 'getUserMedia' not in face)
print('C920 default index:', 'FACE_CAMERA_INDEX", "2"' in (ROOT/'backend/voice/face_service.py').read_text())
print('Voice autofill present:', 'applyAutofill' in voice)
print('Manual override protection:', 'voiceDirty' in voice)
print('Voice API route present:', '/api/voice/audio' in app)
print('Face status route present:', '/api/face/status' in app)
if missing:
    raise SystemExit(1)
