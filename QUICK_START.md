# Quick Start Guide - Question Generation & Clarity Detection

## ✅ Implementation Complete!

Your helpdesk chatbot now has two powerful new features:

### 1. **Level-Wise Question Generation**
Automatically generates beginner, intermediate, and advanced questions for every module based on documentation.

### 2. **Query Clarity Detection**
Detects unclear user queries and asks clarifying questions instead of providing potentially incorrect answers.

---

## 🚀 Quick Test

Run the demo to see it in action:

```bash
cd backend
python quick_demo.py
```

Expected output shows:
- ✅ Query clarity detection working
- ✅ Question generation working  
- ✅ Database persistence working

---

## 📚 How to Use

### For End Users (Chat Interface)

**Clarity Detection is Automatic!**

When users type unclear queries like:
- "help"
- "how to?"
- "it not working"

The chatbot will automatically ask:
```
I'd like to help you better! To provide the most accurate answer, could you clarify:

1. What specific topic would you like help with?
2. Which module are you working with?
3. What are you trying to accomplish?
```

### For Administrators (API)

#### Generate Questions for a Module

```bash
curl -X POST http://localhost:8000/questions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "module": "Purchasing",
    "difficulty_level": "all",
    "tenant_id": "default"
  }'
```

Response:
```json
{
  "success": true,
  "module": "Purchasing",
  "questions": {
    "beginner": [
      "What is the Purchasing module?",
      "How do I create a purchase order?"
    ],
    "intermediate": [
      "How do I manage vendors?",
      "What is the RFQ process?"
    ],
    "advanced": [
      "How do I configure approval workflows?",
      "How do I integrate with Finance?"
    ]
  }
}
```

#### Check Query Clarity

```bash
curl -X POST http://localhost:8000/questions/check-clarity \
  -H "Content-Type: application/json" \
  -d '"help me with setup"'
```

#### Get Random Questions

```bash
curl http://localhost:8000/questions/random/Purchasing?count=3
```

---

## 🔧 Configuration

### Model Settings (Already Configured)

Your `.env` file now has:
```env
GPT_MODEL=gpt-4.1
OPENAI_API_KEY=your_api_key_here
```

All AI operations now use **GPT-4.1** for better quality.

### Adjust Clarity Threshold

Edit `backend/llm/rag.py` line ~230:

```python
if not is_clear and clarity_score < 0.6:  # Default: 0.6
```

Lower = More lenient (0.4-0.5)
Higher = More strict (0.7-0.8)

---

## 📊 API Endpoints

### New Endpoints Added

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/questions/generate` | Generate questions for a module |
| POST | `/questions/generate-all` | Generate for all modules |
| GET | `/questions/list/{module}` | Get saved questions |
| GET | `/questions/random/{module}` | Get random questions |
| POST | `/questions/check-clarity` | Check query clarity |
| GET | `/questions/stats` | Get usage statistics |

### Enhanced Endpoint

| Method | Endpoint | Enhancement |
|--------|----------|-------------|
| POST | `/chat/query` | Now includes automatic clarity detection |

---

## 🗄️ Database

### Tables Created

Two new tables have been initialized:

1. **generated_questions** - Stores all generated questions
2. **query_clarifications** - Tracks clarification requests

To reinitialize tables:
```bash
cd backend
python scripts/init_question_tables.py
```

---

## 📖 Documentation

### Detailed Guides

- **Full Documentation**: `backend/QUESTION_SYSTEM_GUIDE.txt`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Test Suite**: `backend/test_question_system.py`

### API Documentation

Start the server and visit:
```
http://localhost:8000/docs
```

Look for the "Questions" section to see all new endpoints with interactive testing.

---

## 🎯 Usage Examples

### Example 1: Generate Questions When Loading Documentation

After uploading new documentation:

```python
from llm.question_generator import generate_module_questions
from llm.rag import search

# Get documentation context
docs = search("What is Sales module?", "default")
context = "\n".join(docs)

# Generate questions
questions = generate_module_questions("Sales", context, "all")

# Save to database
from database.db_manager import db_manager
db_manager.save_generated_questions("Sales", questions, "default")
```

### Example 2: Check Clarity Before Processing

```python
from llm.clarity_detector import analyze_query_clarity

query = "help me"
analysis = analyze_query_clarity(query)

if not analysis["is_clear"]:
    # Ask user for clarification
    print("Please clarify:", analysis["suggestions"])
else:
    # Process normally
    ...
```

### Example 3: Show Random Questions to Users

```python
from database.db_manager import db_manager
import random

# Get questions for a module
questions = db_manager.get_generated_questions(
    module_name="Purchasing",
    difficulty_level="beginner",
    tenant_id="default"
)

# Show 3 random ones
random_qs = random.sample(questions, 3)
for q in random_qs:
    print(f"- {q['question']}")
```

---

## ✨ Benefits

### For Users
- 🎯 Get help even when unsure what to ask
- 📚 Discover features through suggested questions
- ✅ Receive more accurate answers
- 🚀 Learn progressively (beginner → advanced)

### For Administrators
- 📊 Track unclear queries
- 🔍 Identify documentation gaps
- 📈 Monitor question popularity
- 🎓 Create training materials

---

## 🐛 Troubleshooting

### Problem: Questions Not Generating
**Solution**: Ensure documentation is uploaded for the module first

### Problem: Clarity Detection Too Sensitive
**Solution**: Lower threshold in `backend/llm/rag.py` (e.g., 0.6 → 0.4)

### Problem: Database Errors
**Solution**: Run `python scripts/init_question_tables.py`

### Problem: API Key Errors
**Solution**: Verify `OPENAI_API_KEY` in `.env` file

---

## 🔄 What Changed

### Files Created (8)
- `backend/llm/question_generator.py`
- `backend/llm/clarity_detector.py`
- `backend/routers/questions.py`
- `backend/scripts/init_question_tables.py`
- `backend/test_question_system.py`
- `backend/quick_demo.py`
- `backend/.env`
- Database tables: `generated_questions`, `query_clarifications`

### Files Modified (5)
- `backend/config.py` - Added GPT_MODEL
- `backend/llm/classifier.py` - Use GPT_MODEL
- `backend/llm/rag.py` - Added clarity detection
- `backend/database/db_manager.py` - Added question methods
- `backend/app.py` - Registered questions router

---

## 🎉 You're All Set!

The system is **fully functional** and **ready to use**!

### Next Steps

1. **Start the server**:
   ```bash
   cd backend
   python -m uvicorn app:app --reload --port 8000
   ```

2. **Test the API**: Visit `http://localhost:8000/docs`

3. **Generate questions**: POST to `/questions/generate`

4. **Chat with bot**: POST to `/chat/query` (clarity detection is automatic!)

---

## 💡 Pro Tips

1. **Generate questions after each documentation upload** to keep them fresh
2. **Monitor `/questions/stats`** to see which questions are popular
3. **Adjust clarity threshold** based on your users' feedback
4. **Use random questions** to engage users who don't know what to ask

---

## 📞 Need Help?

- Check: `backend/QUESTION_SYSTEM_GUIDE.txt`
- Run: `backend/test_question_system.py`
- Demo: `backend/quick_demo.py`
- API Docs: `http://localhost:8000/docs`

---

**Status**: ✅ **FULLY IMPLEMENTED AND TESTED**

Enjoy your enhanced helpdesk chatbot! 🎊

