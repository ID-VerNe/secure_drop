@echo off
TITLE SecureDrop Server

echo Activating virtual environment...
REM This assumes the .venv folder is in the project root directory.
call .venv\Scripts\activate.bat

echo Changing to the backend directory...
cd secure-drop-backend

echo Starting SecureDrop FastAPI server on http://0.0.0.0:8000
uvicorn main:app --host 0.0.0.0 --port 8000

echo Server stopped.
pause
