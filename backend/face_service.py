import cv2
import os

def start_camera():
    pass

def camera_status():
    return {"ready": True, "present": False, "recognized": False, "patient": None, "message": "Camera ready"}

def latest_frame():
    return None

def identify(img):
    return None

def enroll(patient_id, img):
    return True

def enroll_from_camera(patient_id):
    return True
