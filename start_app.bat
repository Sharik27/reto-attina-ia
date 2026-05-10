@echo off
setlocal

cd /d "%~dp0"

echo Iniciando Atinna Core...

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo No se encontro venv\Scripts\activate.bat. Se usara el Python disponible en PATH.
)

echo Servidor iniciado en http://127.0.0.1:8000
start "" "http://127.0.0.1:8000/"

python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000

endlocal
