#!/usr/bin/env bash
# Khoi dong ung dung tren macOS/Linux (tuong duong start.bat)
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv || { echo "Khong the tao moi truong ao. Kiem tra Python 3.11+."; exit 1; }
fi
.venv/bin/python -m pip install -r requirements.txt || { echo "Khong the cai dependency. Kiem tra ket noi Internet lan cai dau."; exit 1; }
.venv/bin/python seed.py

echo "Mo trinh duyet tai http://127.0.0.1:${PORT:-8000}"
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8000}"
