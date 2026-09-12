@echo off
echo ===================================================
echo     Launching Vadakkunokki.ai Development Suite
echo ===================================================

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r backend\requirements.txt
) else (
    call .venv\Scripts\activate
)

echo Starting Backend Server (FastAPI on http://127.0.0.1:8000)...
start "Vadakkunokki Backend" cmd /k ".venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000"

echo Starting Frontend Dev Server (Vite on http://localhost:5173)...
cd frontend
start "Vadakkunokki Frontend" cmd /k "npm run dev"

echo Both servers started!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
