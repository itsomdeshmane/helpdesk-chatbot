#!/bin/bash
# Development startup script for Linux/Mac

echo "============================================================"
echo "AI HELPDESK CHATBOT - DEVELOPMENT MODE"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "NOTE: No virtual environment found. Using system Python."
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Using default configuration. See .env.example for options."
    echo ""
fi

echo "Configuration:"
echo "  - Environment: DEVELOPMENT"
echo "  - Host: localhost"
echo "  - Port: 8000"
echo "  - Auto-reload: ENABLED"
echo "  - Logs: logs/"
echo ""
echo "Server URLs:"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:4200"
echo ""
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

# Start the server with auto-reload for development
uvicorn app:app --reload --port 8000


