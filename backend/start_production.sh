#!/bin/bash
# Production startup script for Linux/Mac

echo "============================================================"
echo "AI HELPDESK CHATBOT - PRODUCTION MODE"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "WARNING: No virtual environment found. Consider creating one."
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with required configuration."
    echo "See .env.example for reference."
    echo ""
    exit 1
fi

# Set production environment
export ENVIRONMENT=production

echo ""
echo "Configuration:"
echo "  - Environment: PRODUCTION"
echo "  - Host: 0.0.0.0 (accessible from network)"
echo "  - Port: 8000"
echo "  - Workers: 4"
echo "  - Logs: logs/"
echo ""
echo "Starting server..."
echo "============================================================"
echo ""

# Start with multiple workers for production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4


