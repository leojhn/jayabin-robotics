"""Backend-only camera and face recognition for the Marykutty kiosk."""
from pathlib import Path
import os
import threading
import time
import io

import numpy as np

try:
    import cv2
except Exception as exc:
    cv2 = None
    _CV_ERROR = exc
else:
    _CV_ERROR = None

try:
    import face_recognition
except Exception as exc:
    face_recognition = None
    _FR_ERROR = exc
else:
    _FR_ERROR = None

BASE = Path(__file__).resolve().parents[1] / "face_registry"
BASE.mkdir(parents=True, exist_ok=True)
TOLERANCE = float(os.getenv("FACE_MATCH_TOLERANCE", "0.48"))
CAMERA_INDEX = int(os.getenv("FACE_CAMERA_INDEX", "2"))
CAMERA_DEVICE = os.getenv("FACE_CAMERA_DEVICE", "").strip()
CAMERA_NAME_HINT = os.getenv("FACE_CAMERA_NAME", "C920").strip().casefold()
CAMERA_WIDTH = int(os.getenv("FACE_CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("FACE_CAMERA_HEIGHT", "480"))
SCAN_INTERVAL = float(os.getenv("FACE_SCAN_INTERVAL", "0.6"))
UNKNOWN_AFTER = float(os.getenv("FACE_UNKNOWN_AFTER", "3.0"))

_lock = threading.Lock()
_camera = None
_camera_thread = None
_camera_running = False
_latest_jpeg = None
_latest_result = {
    "ready": False, "recognized": False, "present": False,
    "new_patient": False, "faces": 0, "message": "Starting camera…",
    "known_patients": 0,
}
_last_scan = 0.0
_present_since = None
_known_cache = {}
_known_signature = None


def _require():
    if face_recognition is None:
        raise RuntimeError(
            "Face recognition is not installed. Run: python3 -m pip install face-recognition"
        )


def _require_camera():
    if cv2 is None:
        raise RuntimeError(
            "OpenCV is not installed. Run: python3 -m pip install opencv-python"
        )


def _camera_candidates():
    """Return V4L2 devices, preferring an explicitly named Logitech C920.

    A numeric /dev/videoN index can change when the laptop webcam, C920,
    media nodes, or USB devices are enumerated in a different order.
    Therefore the C920 name is authoritative and the numeric index is only
    the fallback.
    """
    candidates = []
    if CAMERA_DEVICE:
        candidates.append(CAMERA_DEVICE)

    by_id = Path("/dev/v4l/by-id")
    if by_id.exists():
        for link in sorted(by_id.iterdir()):
            try:
                target = str(link.resolve())
            except Exception:
                continue
            if CAMERA_NAME_HINT and CAMERA_NAME_HINT in link.name.casefold():
                candidates.append(target)

    video_root = Path("/sys/class/video4linux")
    named = []
    numeric = []
    if video_root.exists():
        for node in sorted(video_root.glob("video*")):
            name_file = node / "name"
            try:
                name = name_file.read_text(errors="ignore").strip()
            except Exception:
                name = ""
            dev = f"/dev/{node.name}"
            if CAMERA_NAME_HINT and CAMERA_NAME_HINT in name.casefold():
                named.append(dev)
            else:
                numeric.append(dev)
    candidates.extend(named)
    fallback = f"/dev/video{CAMERA_INDEX}"
    candidates.append(fallback)
    candidates.extend(numeric)

    out=[]
    for item in candidates:
        if item and item not in out:
            out.append(item)
    return out


def _open_camera():
    _require_camera()
    errors=[]
    for device in _camera_candidates():
        cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                print(f"[FACE] Using patient camera: {device}")
                return cap, device
        errors.append(device)
        try:
            cap.release()
        except Exception:
            pass
    raise RuntimeError("Could not open Logitech C920 patient camera. Tried: " + ", ".join(errors))


def _decode_image(raw: bytes):
    _require_camera()
    array = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode camera image.")
    return image


def _rgb(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(rgb, dtype=np.uint8)


def _registry_files():
    return sorted([
        p for p in BASE.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ])


def _load_known(force=False):
    global _known_cache, _known_signature
    files = _registry_files()
    signature = tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in files)
    if not force and signature == _known_signature:
        return _known_cache

    cache = {}
    for path in files:
        try:
            image = face_recognition.load_image_file(str(path))
            locations = face_recognition.face_locations(image, model="hog")
            if len(locations) != 1:
                continue
            encodings = face_recognition.face_encodings(image, known_face_locations=locations)
            if encodings:
                cache[path.stem.upper()] = encodings[0]
        except Exception as exc:
            print(f"[FACE] Skipping {path.name}: {exc}")

    _known_cache = cache
    _known_signature = signature
    print(f"[FACE] Loaded {len(cache)} enrolled patient face(s).")
    return cache


def enroll(patient_id: str, raw: bytes):
    _require()
    patient_id = str(patient_id or "").strip().upper()
    if not patient_id:
        raise ValueError("patient_id is required")
    image = _decode_image(raw)
    rgb = _rgb(image)
    locations = face_recognition.face_locations(rgb, model="hog")
    if len(locations) != 1:
        raise ValueError("Please capture exactly one clear face for registration.")
    enc = face_recognition.face_encodings(rgb, known_face_locations=locations)
    if not enc:
        raise ValueError("Could not create a face profile from this photo.")
    path = BASE / f"{patient_id}.jpg"
    cv2.imwrite(str(path), image, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    _load_known(force=True)
    return {"patient_id": patient_id, "path": str(path), "faces": 1}


def identify(raw: bytes):
    _require()
    image = _decode_image(raw)
    rgb = _rgb(image)
    locations = face_recognition.face_locations(rgb, model="hog")
    faces = len(locations)
    if faces != 1:
        return {"recognized": False, "reason": "one_face_required", "faces": faces}

    encodings = face_recognition.face_encodings(rgb, known_face_locations=locations)
    if not encodings:
        return {"recognized": False, "reason": "encoding_failed", "faces": 1}
    probe = encodings[0]

    known = _load_known()
    if not known:
        return {"recognized": False, "reason": "no_enrolled_patients", "faces": 1}

    ids = list(known.keys())
    vectors = list(known.values())
    distances = face_recognition.face_distance(vectors, probe)
    best_index = int(np.argmin(distances))
    best_distance = float(distances[best_index])
    best_id = ids[best_index]

    if best_distance <= TOLERANCE:
        return {
            "recognized": True,
            "patient_id": best_id,
            "distance": round(best_distance, 4),
            "confidence": round(max(0.0, min(1.0, 1.0 - best_distance)), 3),
            "faces": 1,
        }

    return {
        "recognized": False,
        "distance": round(best_distance, 4),
        "faces": 1,
        "reason": "no_match",
    }


def _set_result(result):
    global _latest_result
    with _lock:
        _latest_result = dict(result)


def _camera_loop():
    global _camera, _camera_running, _latest_jpeg, _last_scan, _present_since
    try:
        _require_camera()
        _require()
        _load_known(force=True)
        cap, camera_device = _open_camera()

        _camera = cap
        _camera_running = True
        _set_result({"ready": True, "recognized": False, "present": False, "new_patient": False, "faces": 0, "message": f"Checking patient record using {camera_device}…", "camera_device": camera_device, "known_patients": len(_known_cache)})

        while _camera_running:
            ok, frame = cap.read()
            if not ok:
                _set_result({"ready": False, "recognized": False, "present": False, "new_patient": False, "faces": 0, "message": "Camera frame unavailable.", "known_patients": len(_known_cache)})
                time.sleep(0.5)
                continue

            ok_jpg, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if ok_jpg:
                with _lock:
                    _latest_jpeg = encoded.tobytes()

            now = time.time()
            if now - _last_scan >= SCAN_INTERVAL:
                _last_scan = now
                try:
                    if ok_jpg:
                        result = identify(encoded.tobytes())
                    else:
                        result = {"recognized": False, "faces": 0, "reason": "encode_failed"}
                    result["ready"] = True
                    result["present"] = int(result.get("faces", 0)) == 1
                    result["known_patients"] = len(_known_cache)
                    if result.get("recognized"):
                        _present_since = now
                        result["new_patient"] = False
                        result["message"] = "Patient identified."
                    elif result.get("present"):
                        if _present_since is None:
                            _present_since = now
                        elapsed = now - _present_since
                        result["new_patient"] = elapsed >= UNKNOWN_AFTER
                        result["message"] = "Checking patient record…" if elapsed < UNKNOWN_AFTER else "New patient detected."
                    else:
                        _present_since = None
                        result["new_patient"] = False
                        result["message"] = "Checking patient record…"
                    _set_result(result)
                except Exception as exc:
                    _set_result({"ready": True, "recognized": False, "present": False, "new_patient": False, "faces": 0, "message": str(exc), "known_patients": len(_known_cache)})
            time.sleep(0.01)
    except Exception as exc:
        _set_result({"ready": False, "recognized": False, "present": False, "new_patient": False, "faces": 0, "message": str(exc), "known_patients": len(_known_cache)})
    finally:
        _camera_running = False
        if _camera is not None:
            try:
                _camera.release()
            except Exception:
                pass
        _camera = None


def start_camera():
    global _camera_thread, _camera_running
    with _lock:
        if _camera_thread and _camera_thread.is_alive():
            return
        _camera_running = True
        _camera_thread = threading.Thread(target=_camera_loop, name="patient-face-camera", daemon=True)
        _camera_thread.start()


def stop_camera():
    global _camera_running
    _camera_running = False


def camera_status():
    with _lock:
        return dict(_latest_result)


def latest_frame():
    with _lock:
        return _latest_jpeg


def enroll_from_camera(patient_id: str):
    frame = latest_frame()
    if not frame:
        raise RuntimeError("The backend camera has no frame yet. Please wait a moment and try again.")
    return enroll(patient_id, frame)
