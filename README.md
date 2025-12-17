# AI Helpdesk Chatbot

A multi-tenant AI-powered helpdesk chatbot with document ingestion and RAG capabilities.

## 📚 Documentation

**All documentation has been organized in the `documentation/` folder!**

- **[📋 Complete Documentation Index](documentation/INDEX.md)** - Start here! Complete organized index
- **[📖 Documentation Overview](documentation/README.md)** - Overview and navigation guide
- **[🚀 Quick Start Guide](documentation/QUICK_START.md)** - Get started quickly
- **[📜 Scripts Complete Guide](documentation/scripts/SCRIPTS_COMPLETE_GUIDE.md)** - All 20+ scripts documented
- **[✅ Installation Checklist](documentation/INSTALLATION_CHECKLIST.md)** - Step-by-step setup
- **[📘 Complete System Documentation](documentation/COMPLETE_SYSTEM_DOCUMENTATION.md)** - Comprehensive reference

### Quick Links by Topic
- **Setup & Configuration:** [documentation/setup/](documentation/setup/)
- **Database:** [documentation/database/](documentation/database/)
- **Scripts:** [documentation/scripts/](documentation/scripts/)
- **Deployment:** [documentation/deployment/](documentation/deployment/)
- **Troubleshooting:** [documentation/troubleshooting/](documentation/troubleshooting/)

## Project Structure

```
helpdesk-chatbot/
├── documentation/    # 📚 All documentation (START HERE!)
│   ├── INDEX.md                    # Complete organized index
│   ├── README.md                   # Documentation overview
│   ├── setup/                      # Setup & configuration guides
│   ├── database/                   # Database documentation
│   ├── scripts/                    # Scripts documentation
│   ├── deployment/                 # Deployment guides
│   └── troubleshooting/            # Error guides
├── backend/          # FastAPI backend
│   ├── app.py       # Main FastAPI application
│   ├── routers/     # API route handlers
│   ├── llm/         # LLM and RAG logic
│   ├── ingestion/   # Document processing
│   └── scripts/     # Utility scripts
├── frontend/         # React frontend
│   └── src/         # React components
└── docs/            # Source documents (Verax workflows)
```

## Quick Setup

For complete setup instructions, see **[Installation Checklist](documentation/INSTALLATION_CHECKLIST.md)** and **[Quick Start Guide](documentation/QUICK_START.md)**.

### Quick Start

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Add your API keys (OpenAI, Pinecone, etc.)
   - See [Environment Setup Guide](documentation/setup/ENV_SETUP_GUIDE.md)

3. **Setup database:**
   ```bash
   # Run migrations (IMPORTANT!)
   python scripts/migrate_all_conversation_features.py
   ```
   See [Database Migrations Guide](documentation/database/DATABASE_MIGRATIONS_GUIDE.md)

4. **Load documents:**
   ```bash
   python scripts/reload_verax_docs.py
   ```
   See [Scripts Guide](documentation/scripts/SCRIPTS_COMPLETE_GUIDE.md)

5. **Start backend:**
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

See `backend/.env.example` for required environment variables, or check the **[Environment Setup Guide](documentation/setup/ENV_SETUP_GUIDE.md)** for detailed configuration instructions.

## Documentation & Help

- **📋 Start Here:** [Complete Documentation Index](documentation/INDEX.md)
- **🚀 Quick Setup:** [Quick Start Guide](documentation/QUICK_START.md)
- **📜 Scripts:** [Scripts Complete Guide](documentation/scripts/SCRIPTS_COMPLETE_GUIDE.md) - All utility scripts documented
- **🗄️ Database:** [Database Migrations Guide](documentation/database/DATABASE_MIGRATIONS_GUIDE.md)
- **🔧 Troubleshooting:** [Troubleshooting Guides](documentation/troubleshooting/)
- **📘 Complete Docs:** [Complete System Documentation](documentation/COMPLETE_SYSTEM_DOCUMENTATION.md)

## Features

- 🤖 **AI-Powered Chat** - Smart conversational interface with context awareness
- 📄 **Document Ingestion** - Support for PDF, DOCX, Excel, Markdown, and TXT files
- 🔍 **Smart Search** - Hybrid search with vector embeddings and keyword matching
- 🧠 **Intelligent Entity Matching** - Fuzzy matching and context-based entity recognition
- 💬 **Multi-Turn Conversations** - Session management with conversation memory
- ❓ **Question Generation** - AI-generated related and clarifying questions
- 🏢 **Multi-Tenant** - Support for multiple organizations
- 🔐 **Authentication** - JWT-based secure authentication
- 📊 **Analytics** - Query pattern analysis and conversation tracking

See [Enhanced Features Guide](documentation/ENHANCED_FEATURES_GUIDE.md) for details.

## Scripts & Utilities

The system includes 20+ utility scripts for database management, migrations, data loading, and more.

**See [Scripts Complete Guide](documentation/scripts/SCRIPTS_COMPLETE_GUIDE.md)** for comprehensive documentation of all scripts.

Common scripts:
- `clear_database.py` - Database management
- `migrate_all_conversation_features.py` - Setup conversations (RUN FIRST!)
- `reload_verax_docs.py` - Load documents
- `setup_pinecone.py` - Setup vector database
- And many more...

## Support

For help and troubleshooting:
1. Check [Documentation Index](documentation/INDEX.md)
2. Review [Troubleshooting Guides](documentation/troubleshooting/)
3. See [Scripts Guide](documentation/scripts/SCRIPTS_COMPLETE_GUIDE.md) for script issues
4. Check [Complete System Documentation](documentation/COMPLETE_SYSTEM_DOCUMENTATION.md)

