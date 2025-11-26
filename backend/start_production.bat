@echo off
REM Production startup script for Windows
echo ============================================================
echo AI HELPDESK CHATBOT - PRODUCTION MODE
echo ============================================================
echo.

REM Check if virtual environment exists
if exist venv\ (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: No virtual environment found. Consider creating one.
    echo.
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file with required configuration.
    echo See .env.example for reference.
    echo.
    pause
    exit /b 1
)

REM Set production environment
set ENVIRONMENT=production

echo.
echo Configuration:
echo   - Environment: PRODUCTION
echo   - Host: 0.0.0.0 (accessible from network)
echo   - Port: 8000
echo   - Workers: 4
echo   - Logs: logs/
echo.
echo Starting server...
echo ============================================================
echo.

REM Start with multiple workers for production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

pause


