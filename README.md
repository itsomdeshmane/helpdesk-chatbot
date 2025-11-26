# AI Helpdesk Chatbot

A multi-tenant AI-powered helpdesk chatbot with document ingestion and RAG capabilities.

## Project Structure

```
helpdesk/
├── backend/          # FastAPI backend
│   ├── app.py       # Main FastAPI application
│   ├── routers/     # API route handlers
│   ├── llm/         # LLM and RAG logic
│   └── ingestion/   # Document processing
└── frontend/         # React frontend
    └── src/         # React components
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file from the example:
   ```bash
   copy .env.example .env
   ```
   
6. Edit `.env` and add your API keys

7. Run the backend:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the frontend:
   ```bash
   npm start
   ```

The frontend will run on http://localhost:3000 and proxy API requests to the backend on http://localhost:8000.

## API Endpoints

- `GET /` - Health check
- `POST /chat/query` - Send chat query
- `POST /documents/upload` - Upload and index documents

## Environment Variables

See `backend/.env.example` for required environment variables.

