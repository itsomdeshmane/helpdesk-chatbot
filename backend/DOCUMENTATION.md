# Backend Documentation

**All documentation has been moved to the centralized `docs/` folder.**

## 📚 Quick Links

### For Backend Developers
- **Complete System Documentation**: [`../docs/COMPLETE_SYSTEM_DOCUMENTATION.md`](../docs/COMPLETE_SYSTEM_DOCUMENTATION.md)
- **Database Documentation**: [`../docs/database/`](../docs/database/)
- **Authentication Setup**: [`../docs/setup/`](../docs/setup/)

### For Database Work
- **Migration Guide**: [`../docs/database/DATABASE_MIGRATIONS_GUIDE.md`](../docs/database/DATABASE_MIGRATIONS_GUIDE.md)
- **Migration Scripts**: [`database/migrations/`](database/migrations/)
- **Scripts Documentation**: [`../docs/database/SCRIPTS_README.md`](../docs/database/SCRIPTS_README.md)

### For Deployment
- **Production Deployment**: [`../docs/deployment/`](../docs/deployment/)

---

## 📂 Backend Folder Structure

```
backend/
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
│
├── database/                 # Database layer
│   ├── db_manager.py        # Database manager
│   └── migrations/          # SQL migration scripts
│
├── routers/                  # API endpoints
│   ├── auth.py              # Authentication routes
│   ├── chat.py              # Chat endpoints
│   ├── documents.py         # Document management
│   ├── questions.py         # Question generation
│   └── analytics.py         # Analytics endpoints
│
├── llm/                      # AI/LLM components
│   ├── rag.py               # RAG system
│   ├── prompt_enhancer.py   # Prompt engineering
│   ├── classifier.py        # Module classification
│   └── question_generator.py
│
├── ingestion/                # Document processing
│   ├── docs_loader.py       # Document loader
│   ├── chunker.py           # Text chunking (semantic)
│   └── [readers]            # PDF, DOCX, Excel readers
│
├── utils/                    # Utilities
│   ├── auth.py              # Auth utilities
│   ├── conversation_manager.py
│   └── logger.py
│
└── scripts/                  # Database & setup scripts
    ├── run_migrations.py
    ├── create_users_table.py
    └── [various utilities]
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
cd database/migrations
python run_migrations.py
```

### 3. Create Admin User
```bash
cd scripts
python create_users_table.py
```

### 4. Run Server
```bash
# Development
uvicorn app:app --reload

# Production
./start_production.sh
```

---

## 📖 Full Documentation

**All comprehensive documentation is located in:**
👉 [`../docs/`](../docs/)

**Start with:** [`../docs/README.md`](../docs/README.md)

---

**For backend-specific README:** See this file (you're reading it!)
**For complete system docs:** See [`../docs/`](../docs/)


