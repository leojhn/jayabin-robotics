#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --upgrade pip
python3 -m pip install requests python-dotenv Pillow==12.3.0 opencv-python==4.12.0.88
python3 -m pip install face-recognition==1.3.0

mkdir -p backend/face_registry
chmod 700 backend/face_registry

if [ ! -f .env ]; then
  cp SARVAM_ENV.example .env
  echo
  echo "Created .env from SARVAM_ENV.example."
  echo "Edit .env and set SARVAM_API_KEY before using voice."
fi

echo
echo "Camera + voice dependencies installed."
echo "C920 default: /dev/video2 (FACE_CAMERA_INDEX=2)"
echo "Start HMS with:"
echo "  cd backend"
echo "  python3 -m app"
