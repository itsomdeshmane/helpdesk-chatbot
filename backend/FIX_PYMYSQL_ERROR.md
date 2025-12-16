# Fix PyMySQL Installation Error

## Problem
```
ModuleNotFoundError: No module named 'pymysql'
```

## Solution Options

### ✅ Option 1: Install PyMySQL (Recommended)

Open Command Prompt or PowerShell and run:

```bash
# Navigate to backend directory
cd c:\projects\helpdesk\helpdesk-chatbot\backend

# Install pymysql
pip install pymysql

# Verify installation
python -c "import pymysql; print('Success!')"
```

### ✅ Option 2: Install All Requirements

```bash
cd c:\projects\helpdesk\helpdesk-chatbot\backend
pip install -r requirements.txt
```

### ✅ Option 3: Run Installation Script

```bash
cd c:\projects\helpdesk\helpdesk-chatbot\backend
python install_pymysql.py
```

---

## 🔍 Troubleshooting

### Issue: "pip is not recognized"

Use Python module syntax:
```bash
python -m pip install pymysql
```

### Issue: "Permission denied"

Run as administrator or use:
```bash
pip install --user pymysql
```

### Issue: Multiple Python versions

Make sure you're using the correct Python:
```bash
# Check Python version
python --version

# Install for specific Python
py -3.12 -m pip install pymysql
```

### Issue: Virtual environment

If using a virtual environment:
```bash
# Activate venv first
cd c:\projects\helpdesk\helpdesk-chatbot\backend
.\venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Then install
pip install pymysql
```

---

## 🚀 After Installation

### Start Backend Server

```bash
cd c:\projects\helpdesk\helpdesk-chatbot\backend
python -m uvicorn app:app --reload --port 8000
```

You should see:
```
AI HELPDESK CHATBOT - READY!
Backend: http://localhost:8000
```

### Test Smart Chat

Open another terminal and test:
```bash
curl http://localhost:8000/health
```

---

## ⚠️ Still Not Working?

### Option A: Disable Database Features Temporarily

If you only want to use the document search features (not database analytics), you can temporarily disable the smart chat router:

1. Open `backend/app.py`
2. Comment out this line:
   ```python
   # app.include_router(smart_chat.router, prefix="/chat")
   ```
3. Restart the backend

This will let you use the document search while you fix pymysql.

### Option B: Check Python Environment

```bash
# Check which Python is being used
where python

# Check if pymysql is visible to Python
python -c "import sys; print('\n'.join(sys.path))"

# Try installing with full path
C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe -m pip install pymysql
```

---

## 📦 Requirements File

Make sure `requirements.txt` includes:
```
pymysql==1.1.0
```

---

## ✅ Verification

After fixing, verify everything works:

```bash
# Test import
python -c "import pymysql; print('✅ PyMySQL OK')"

# Test services
python -c "from llm.database_query_service import get_database_query_service; print('✅ Database service OK')"

# Test router
python -c "from routers.smart_chat import router; print('✅ Smart chat router OK')"

# Start server
python -m uvicorn app:app --reload --port 8000
```

---

## 💬 Need More Help?

If none of these solutions work:

1. Check your Python version: `python --version` (need 3.9+)
2. Check pip version: `pip --version`
3. Try upgrading pip: `python -m pip install --upgrade pip`
4. Check for conflicting packages: `pip list | findstr mysql`
5. Try in a fresh virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install pymysql
   ```

---

## 🎉 Success!

Once pymysql is installed, you can:
- ✅ Use document search (existing feature)
- ✅ Use database analytics (new feature)
- ✅ Use smart multi-source chat
- ✅ Query database with natural language

Enjoy your Smart Chat AI Assistant! 🚀

