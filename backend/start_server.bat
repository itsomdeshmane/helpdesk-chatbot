@echo off
REM Development startup script for Windows
echo ============================================================
echo AI HELPDESK CHATBOT - DEVELOPMENT MODE
echo ============================================================
echo.

REM Check if virtual environment exists
if exist venv\ (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo NOTE: No virtual environment found. Using system Python.
    echo.
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Using default configuration. See .env.example for options.
    echo.
)

echo Configuration:
echo   - Environment: DEVELOPMENT
echo   - Host: localhost
echo   - Port: 8000
echo   - Auto-reload: ENABLED
echo   - Logs: logs/
echo.
echo Server URLs:
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:4200
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

REM Start the server with auto-reload for development
cd /d "%~dp0"
uvicorn app:app --reload --port 8000

pause

