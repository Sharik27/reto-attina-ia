#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "Iniciando Atinna Core..."

if [ -f "venv/Scripts/activate" ]; then
  source "venv/Scripts/activate"
else
  echo "No se encontro venv/Scripts/activate. Se usara el Python disponible en PATH."
fi

python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

python - <<'PY'
import sys
import time
import urllib.request

url = "http://127.0.0.1:8000/health"
for _ in range(30):
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if response.status == 200:
                sys.exit(0)
    except Exception:
        time.sleep(1)

print("No se pudo confirmar que el servidor iniciara en http://127.0.0.1:8000")
sys.exit(1)
PY

echo "Servidor iniciado en http://127.0.0.1:8000"

if command -v cmd.exe >/dev/null 2>&1; then
  cmd.exe /c start "" "http://127.0.0.1:8000/" >/dev/null 2>&1 || true
fi

wait "$SERVER_PID"
