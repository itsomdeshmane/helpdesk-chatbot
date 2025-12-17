# Quick Start Guide - Smart Chat AI Assistant

Get up and running with the Smart Chat AI Assistant in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Node.js 16+ installed
- MySQL 8.0+ installed (optional, for database analytics)
- OpenAI API key

## Step 1: Clone & Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
# Copy the template and fill in your API keys
# See ENV_SETUP_GUIDE.md for details
```

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-env
PINECONE_INDEX_NAME=helpdesk-docs

# Optional: For database analytics
DB_HOST=localhost
DB_NAME=helpdesk_db
DB_USER=root
DB_PASSWORD=your_password

JWT_SECRET_KEY=your-secret-key-change-this
```

## Step 2: Start Backend Server

```bash
# In backend directory
python -m uvicorn app:app --reload --port 8000
```

You should see:
```
AI HELPDESK CHATBOT - READY!
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
```

## Step 3: Setup Frontend

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Browser will open at `http://localhost:3000`

## Step 4: First Login

Default credentials:
- Username: `admin`
- Password: `admin123`

Or register a new account!

## Step 5: Try It Out!

### Test Document Search:
1. Click "📄 Docs" source button
2. Ask: "How do I use the system?"

### Test Database Analytics:
1. Click "💾 Database" source button
2. Ask: "How many customers do we have?"

### Test Smart Mode:
1. Click "⚡ Auto" source button
2. Ask any question - system will automatically choose the best source!

## Example Queries

### Document Queries (📄 Docs):
- "How do I reset my password?"
- "What are the system requirements?"
- "How do I configure authentication?"

### Database Queries (💾 Database):
- "Show me all customers"
- "How many orders were placed last month?"
- "What is the total revenue?"
- "List top 5 products by sales"

### Smart Mode (⚡ Auto):
- "Tell me about user management" → Searches docs
- "How many users do we have?" → Queries database
- "Show me statistics" → Tries both sources

## Features

✅ **Multi-Source Intelligence**
- Documents (Knowledge Base)
- Database (SQL Analytics)
- Automatic fallback

✅ **Beautiful UI**
- ChatGPT-like interface
- Real-time streaming
- Source selection
- Data tables for results

✅ **Smart Features**
- Context-aware conversations
- Markdown rendering
- Feedback system
- Session management

## Next Steps

### 1. Load Your Documents
```bash
# Upload documents to knowledge base
curl -X POST http://localhost:8000/documents/reload
```

Or use the API docs: http://localhost:8000/docs

### 2. Configure Your Database
If you want database analytics:
1. Create MySQL database
2. Add connection info to `.env`
3. (Optional) Load sample data (see ENV_SETUP_GUIDE.md)

### 3. Customize
- Add your own documents to `docs/` folder
- Configure database schema
- Customize UI colors in CSS
- Add more features!

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check `.env` file exists

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Clear cache: `rm -rf node_modules && npm install`

### "OpenAI API Error"
- Verify API key in `.env`
- Check key is valid at https://platform.openai.com
- Ensure you have credits

### "Database connection failed"
- Check MySQL is running
- Verify credentials in `.env`
- Test connection: `mysql -u root -p`

### "No documents found"
- Load documents: `POST /documents/reload`
- Check Pinecone configuration
- Verify API keys

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Implementation Guide**: See SMART_CHAT_IMPLEMENTATION_GUIDE.md
- **Environment Setup**: See ENV_SETUP_GUIDE.md
- **Backend Logs**: Check terminal where backend is running
- **Frontend Logs**: Check browser console (F12)

## Architecture Overview

```
┌──────────────┐
│   Frontend   │  React + Enhanced UI
│  (Port 3000) │  - Source selection
└──────┬───────┘  - Streaming responses
       │          - ChatGPT-like interface
       │
       ▼
┌──────────────────────────────────────┐
│         Backend (Port 8000)          │
│  ┌────────────────────────────────┐  │
│  │    Smart Chat Router           │  │
│  │   (3-Layer Fallback)           │  │
│  └────────────────────────────────┘  │
│         │          │          │       │
│         ▼          ▼          ▼       │
│    Documents   Database  Clarifying   │
│       RAG        SQL      Questions   │
└──────────────────────────────────────┘
       │          │
       ▼          ▼
   Pinecone    MySQL
   (Vectors)   (Data)
```

## What's Next?

1. **Production Deployment**
   - See PRODUCTION_DEPLOYMENT.md
   - Configure SSL/TLS
   - Set up monitoring

2. **Advanced Features**
   - Fine-tune models
   - Add more data sources
   - Implement caching
   - Add analytics dashboard

3. **Customization**
   - Brand colors and logo
   - Custom prompts
   - Additional sources
   - Role-based access

## Support

This is a production-ready AI assistant combining:
- ✅ .NET Analytics Chatbot features (ported to Python)
- ✅ Existing Python helpdesk capabilities
- ✅ Beautiful ChatGPT-like UI
- ✅ Multi-source intelligence

Enjoy your Smart Chat AI Assistant! 🚀


