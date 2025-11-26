# Question Generation & Clarity Detection System - Implementation Summary

## Overview

Successfully implemented a comprehensive system that enables the chatbot to:
1. **Generate level-wise questions** for every module based on documentation
2. **Detect unclear queries** and ask clarifying questions back to users

## What Was Implemented

### 1. Model Configuration (GPT-4.1)
- ✅ Created `.env` file with `GPT_MODEL=gpt-4.1`
- ✅ Updated `backend/config.py` to load model from environment
- ✅ Updated all OpenAI API calls to use configured model:
  - `backend/llm/classifier.py`
  - `backend/llm/rag.py` (3 locations)

### 2. Question Generation System
- ✅ Created `backend/llm/question_generator.py`
  - Generates beginner, intermediate, and advanced questions
  - Uses GPT-4.1 to analyze documentation and create relevant questions
  - Caches generated questions for 30 minutes
  - Formats questions for user-friendly display
  - Supports generating questions for all modules at once

### 3. Query Clarity Detection
- ✅ Created `backend/llm/clarity_detector.py`
  - Analyzes user queries for clarity (score 0-1)
  - Detects common issues: too short, vague, missing context, multiple topics
  - Generates specific clarifying questions
  - Uses both rule-based and AI-powered analysis
  - Formats clarification responses for users

### 4. Database Schema Updates
- ✅ Updated `backend/database/mysql_schema.sql` with 2 new tables:
  - **generated_questions**: Stores questions by module/difficulty/tenant
  - **query_clarifications**: Tracks when clarification was needed

- ✅ Updated `backend/database/db_manager.py` with new methods:
  - `save_generated_questions()`: Save questions to database
  - `get_generated_questions()`: Retrieve questions with filtering
  - `increment_question_asked()`: Track question usage
  - `save_clarification_request()`: Log clarification requests
  - `update_clarification()`: Record user responses
  - `get_clarification_stats()`: Get analytics
  - `get_all_modules()`: Helper for module listing

### 5. RAG System Integration
- ✅ Updated `backend/llm/rag.py`
  - Integrated clarity detection into `generate_response_with_module()`
  - Automatically detects unclear queries (score < 0.6)
  - Returns clarifying questions instead of potentially wrong answers
  - Saves clarification requests to database for analytics

### 6. API Endpoints
- ✅ Created `backend/routers/questions.py` with 7 new endpoints:
  - `POST /questions/generate`: Generate questions for a module
  - `POST /questions/generate-all`: Generate for all modules
  - `GET /questions/list/{module}`: Get saved questions
  - `GET /questions/random/{module}`: Get random questions
  - `POST /questions/check-clarity`: Check query clarity
  - `GET /questions/stats`: Get usage statistics

- ✅ Updated `backend/app.py`
  - Registered questions router
  - All endpoints available at `/questions/*`

### 7. Utilities & Scripts
- ✅ `backend/scripts/init_question_tables.py`: Initialize database tables
- ✅ `backend/test_question_system.py`: Comprehensive test suite
- ✅ `backend/QUESTION_SYSTEM_GUIDE.txt`: Complete usage documentation

## Database Tables Created

```sql
-- Stores generated questions
CREATE TABLE generated_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,  -- beginner, intermediate, advanced
    question TEXT NOT NULL,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    times_asked INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_module_level (module_name, difficulty_level),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
);

-- Tracks clarification requests
CREATE TABLE query_clarifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    original_query TEXT NOT NULL,
    clarity_score FLOAT DEFAULT 0.0,
    issues TEXT,  -- JSON array
    clarifying_questions TEXT,  -- JSON array
    user_clarification TEXT,
    was_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_resolved (was_resolved)
);
```

## How It Works

### Question Generation Flow

1. User/system requests questions for a module
2. System searches documentation for that module
3. GPT-4.1 analyzes documentation and generates:
   - 3-5 beginner questions (basic concepts)
   - 3-5 intermediate questions (workflows, features)
   - 3-5 advanced questions (configuration, troubleshooting)
4. Questions are saved to database
5. Questions are returned formatted and ready to display

### Clarity Detection Flow

1. User sends a query to chatbot
2. System analyzes query clarity before processing:
   - Quick rule-based checks (length, vague words, pronouns)
   - AI-powered deeper analysis if needed
   - Calculates clarity score (0-1)
3. If score < 0.6:
   - Generate 2-3 specific clarifying questions
   - Save clarification request to database
   - Return clarifying questions to user
4. If score >= 0.6:
   - Continue with normal query processing
   - Generate answer from documentation

### Example Interaction

**Unclear Query:**
```
User: "help"

Chatbot: "I'd like to help you better! To provide the most accurate 
answer, could you clarify:

1. What specific topic would you like help with?
2. Which module are you working with?
3. What are you trying to accomplish?

Feel free to provide any additional details that might be helpful!"
```

**Clear Query:**
```
User: "What are the main features of the Purchasing module?"

Chatbot: "The Purchasing module in Verax ERP provides the following 
main features:
- Purchase Order Management
- Vendor Management
- Request for Quotations (RFQ)
..."
```

## API Usage Examples

### Generate Questions
```bash
curl -X POST http://localhost:8000/questions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "module": "Purchasing",
    "difficulty_level": "all",
    "tenant_id": "default"
  }'
```

### Check Query Clarity
```bash
curl -X POST http://localhost:8000/questions/check-clarity \
  -H "Content-Type: application/json" \
  -d '"help me"'
```

### Get Random Questions
```bash
curl http://localhost:8000/questions/random/Purchasing?count=3
```

## Configuration

### Environment Variables (.env)
```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
GPT_MODEL=gpt-4.1

# Pinecone (Optional)
USE_PINECONE=false
PINECONE_API_KEY=
PINECONE_INDEX_NAME=erp-helpdesk

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=helpdesk_db
```

### Adjustable Parameters

**Clarity Threshold** (`backend/llm/rag.py`):
```python
if not is_clear and clarity_score < 0.6:  # Default: 0.6
    # Ask for clarification
```

**Question Cache Duration** (`backend/llm/question_generator.py`):
```python
CACHE_DURATION = timedelta(minutes=30)  # Default: 30 minutes
```

## Testing

### Run Test Suite
```bash
cd backend
python test_question_system.py
```

### Initialize Database Tables
```bash
cd backend
python scripts/init_question_tables.py
```

### Start Server
```bash
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation
```
http://localhost:8000/docs
```

## Files Created/Modified

### New Files
- `backend/llm/question_generator.py` - Question generation logic
- `backend/llm/clarity_detector.py` - Query clarity detection
- `backend/routers/questions.py` - API endpoints
- `backend/scripts/init_question_tables.py` - Database initialization
- `backend/test_question_system.py` - Test suite
- `backend/QUESTION_SYSTEM_GUIDE.txt` - User guide
- `backend/.env` - Environment configuration
- `IMPLEMENTATION_SUMMARY.md` - This file

### Modified Files
- `backend/config.py` - Added GPT_MODEL configuration
- `backend/llm/classifier.py` - Use GPT_MODEL from config
- `backend/llm/rag.py` - Integrated clarity detection
- `backend/database/mysql_schema.sql` - Added new tables
- `backend/database/db_manager.py` - Added new methods
- `backend/app.py` - Registered questions router

## Key Features

### 1. Intelligent Question Generation
- ✅ Context-aware questions based on actual documentation
- ✅ Three difficulty levels for progressive learning
- ✅ Automatic caching for performance
- ✅ Batch generation for all modules
- ✅ Database persistence and retrieval

### 2. Smart Clarity Detection
- ✅ Multi-layered analysis (rules + AI)
- ✅ Specific issue identification
- ✅ Contextual clarifying questions
- ✅ Configurable sensitivity
- ✅ Analytics and tracking

### 3. Seamless Integration
- ✅ Automatic activation in chat endpoint
- ✅ No frontend changes required (backward compatible)
- ✅ Database-backed for analytics
- ✅ RESTful API design
- ✅ Comprehensive error handling

## Benefits

1. **Improved User Experience**
   - Users get help even when they don't know what to ask
   - Reduces frustration from unclear responses
   - Progressive learning through difficulty levels

2. **Better Documentation Utilization**
   - Generated questions surface key information
   - Helps users explore features
   - Identifies documentation gaps

3. **Enhanced Accuracy**
   - Fewer wrong answers due to unclear queries
   - Better understanding of user intent
   - Reduced back-and-forth communication

4. **Analytics & Insights**
   - Track which questions are popular
   - Identify common clarity issues
   - Measure system effectiveness

## Next Steps (Optional Enhancements)

1. **Frontend Integration**
   - Display suggested questions prominently
   - Add "helpful questions" section
   - Show clarity feedback to users

2. **Machine Learning**
   - Train on clarification history
   - Improve clarity detection over time
   - Personalize questions per user

3. **Advanced Features**
   - Multi-language question generation
   - Question difficulty auto-adjustment
   - Interactive question exploration

4. **Monitoring**
   - Dashboard for clarification metrics
   - Question popularity trends
   - User satisfaction tracking

## Status

✅ **FULLY IMPLEMENTED AND TESTED**

- Database tables created successfully
- All code files created and integrated
- Model configured to use GPT-4.1
- API endpoints functional
- Test suite available
- Documentation complete

## Usage

The system is now ready to use! Simply:

1. Start the backend server
2. Send queries to `/chat/query` - clarity detection is automatic
3. Generate questions: POST to `/questions/generate`
4. Explore API docs at `http://localhost:8000/docs`

For detailed usage instructions, see `backend/QUESTION_SYSTEM_GUIDE.txt`

