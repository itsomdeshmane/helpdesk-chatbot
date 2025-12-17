# Installation Checklist

Use this checklist to ensure everything is set up correctly.

## ✅ Prerequisites

- [ ] Python 3.9+ installed
  ```bash
  python --version
  ```

- [ ] Node.js 16+ installed
  ```bash
  node --version
  ```

- [ ] MySQL 8.0+ installed (optional, for database features)
  ```bash
  mysql --version
  ```

- [ ] Git installed
  ```bash
  git --version
  ```

## ✅ Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import pymysql; import openai; import fastapi; print('✅ All packages installed')"
```

### 2. Create Environment File

Create `backend/.env` file:

```env
# Required
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-env
PINECONE_INDEX_NAME=helpdesk-docs

# Optional (for database features)
DB_HOST=localhost
DB_NAME=helpdesk_db
DB_USER=root
DB_PASSWORD=your_password

# Required
JWT_SECRET_KEY=change-this-secret-key
```

**Verify configuration:**
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ OPENAI_API_KEY:', 'Set' if os.getenv('OPENAI_API_KEY') else 'Not set')"
```

### 3. Test Backend

```bash
python test_smart_chat.py
```

**Expected:** Should show test results (some may fail if DB not configured, that's OK)

### 4. Start Backend Server

**Option A: Using script (Windows)**
```bash
start_backend.bat
```

**Option B: Manual**
```bash
python -m uvicorn app:app --reload --port 8000
```

**Verify:**
- [ ] Server starts without errors
- [ ] Visit http://localhost:8000 - should show `{"status": "running"}`
- [ ] Visit http://localhost:8000/docs - should show API documentation

## ✅ Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

**Verify:**
```bash
npm list react react-dom
```

### 2. Start Frontend

```bash
npm start
```

**Verify:**
- [ ] Browser opens automatically to http://localhost:3000
- [ ] Login page appears
- [ ] No console errors in browser (F12)

## ✅ Database Setup (Optional)

Only needed if you want to use the database analytics feature.

### 1. Create Database

```sql
CREATE DATABASE helpdesk_db;
USE helpdesk_db;
```

### 2. Create Sample Tables

See `ENV_SETUP_GUIDE.md` for SQL scripts to create sample tables.

### 3. Update .env

Make sure these are set in `backend/.env`:
```env
DB_HOST=localhost
DB_NAME=helpdesk_db
DB_USER=root
DB_PASSWORD=your_password
```

### 4. Test Connection

```bash
cd backend
python -c "from llm.schema_service import get_schema_service; import asyncio; asyncio.run(get_schema_service().get_all_tables())"
```

## ✅ First Use

### 1. Login

**Default credentials:**
- Username: `admin`
- Password: `admin123`

Or register a new account.

### 2. Test Document Search

- Click **📄 Docs** button
- Ask: "How do I use the system?"
- Should get a response (or "no documents" message if not loaded)

### 3. Load Documents (Optional)

```bash
curl -X POST http://localhost:8000/documents/reload
```

Or add documents to `docs/` folder.

### 4. Test Database Analytics (if configured)

- Click **💾 Database** button
- Ask: "Show me all tables"
- Should get list of tables or SQL results

### 5. Test Auto Mode

- Click **⚡ Auto** button
- Ask any question
- System will automatically choose best source

## ✅ Verification Commands

Run these to verify everything is working:

### Backend Health
```bash
curl http://localhost:8000/health
```

### Smart Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat/smart/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "source": "auto", "tenant_id": "default"}'
```

### Schema Endpoint (if DB configured)
```bash
curl http://localhost:8000/chat/schema
```

## ✅ Common Issues

### Issue: "ModuleNotFoundError: No module named 'pymysql'"
```bash
cd backend
pip install pymysql
```

### Issue: "OpenAI API key not found"
- Check `backend/.env` file exists
- Verify `OPENAI_API_KEY=sk-...` is set
- Restart backend server

### Issue: Frontend can't connect to backend
- Verify backend is running on port 8000
- Check browser console (F12) for CORS errors
- Verify no firewall blocking localhost

### Issue: "Database connection failed"
- Check MySQL is running
- Verify credentials in `.env`
- Test: `mysql -u root -p`

### Issue: Login fails
- Check backend logs
- Verify JWT_SECRET_KEY is set in `.env`
- Try registering a new account

## ✅ Success Indicators

You're all set when:

- [✅] Backend starts without errors
- [✅] Frontend loads and shows login page
- [✅] Can login successfully
- [✅] Chat interface loads with source selection
- [✅] Can send messages and get responses
- [✅] Source selection buttons work
- [✅] Streaming responses work

## 📚 Next Steps

Once everything is working:

1. Read `QUICK_START.md` for usage guide
2. Read `SMART_CHAT_IMPLEMENTATION_GUIDE.md` for technical details
3. Customize for your needs
4. Add your own documents
5. Configure your database

## 🎉 You're Ready!

If all checkboxes are marked, you have successfully installed the Smart Chat AI Assistant!

For help:
- Check logs in backend terminal
- Check browser console (F12)
- Review documentation files
- Run `python test_smart_chat.py`


