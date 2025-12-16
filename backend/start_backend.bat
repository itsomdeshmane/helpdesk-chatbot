@echo off
echo ========================================
echo Starting AI Smart Chat Backend
echo ========================================
echo.
echo Checking Python installation...
python --version
echo.
echo Checking required packages...
python -c "import pymysql; import openai; import fastapi; print('✅ All core packages installed')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Missing packages. Installing...
    pip install -r requirements.txt
)
echo.
echo Starting server on http://localhost:8000
echo API Docs available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python -m uvicorn app:app --reload --port 8000

