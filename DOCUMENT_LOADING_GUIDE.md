# 📚 Document Loading Guide

## Important Change

**Documents are NO LONGER loaded automatically on application startup.**

This change was made to:
- ✅ Prevent wasteful OpenAI API calls on every restart
- ✅ Avoid re-embedding documents that are already in Pinecone
- ✅ Give you control over when documents are processed
- ✅ Reduce startup time

---

## How to Load Documents

### Option 1: Use the API Endpoints

#### A. Upload a Single Document
```bash
# Upload a PDF, DOCX, XLSX, or TXT file
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@/path/to/your/document.pdf" \
  -F "tenant_id=default"
```

**Example:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@workflow_guide.pdf" \
  -F "tenant_id=default"
```

#### B. Reload All Documents from `docs/` Folder
```bash
# Reload ALL files from docs/ folder (PDF, DOCX, XLSX, TXT, MD)
curl -X POST "http://localhost:8000/documents/reload" \
  -F "tenant_id=default"
```

This will:
- Scan the `docs/` folder
- Process **all** supported files including **markdown (.md)**
- Generate embeddings
- Store in Pinecone/in-memory
- Use structure-aware chunking for markdown files automatically

**Note:** This endpoint now automatically loads markdown files too! No separate call needed.

#### C. Reload Only Markdown Documentation (Optional)
```bash
# Reload ONLY .md files from docs/ folder
curl -X POST "http://localhost:8000/documents/reload-markdown" \
  -F "tenant_id=default"
```

**When to use this:**
- Only markdown files were updated
- You want to skip processing regular files
- Faster reload for markdown-only changes

---

### Option 2: Use Swagger UI

1. Start the backend:
   ```bash
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open Swagger UI:
   ```
   http://localhost:8000/docs
   ```

3. Navigate to **Documents** section

4. Use one of these endpoints:
   - `POST /documents/upload` - Upload single file
   - `POST /documents/reload` - Reload all from docs/
   - `POST /documents/reload-markdown` - Reload markdown files

---

### Option 3: Use Frontend (if available)

If your frontend has document management UI:
1. Go to **Settings** or **Documents** page
2. Click **Upload Documents** or **Reload Documents**
3. Select files or trigger reload

---

## When to Reload Documents

### ✅ You SHOULD reload when:
- Adding new documentation files
- Updating existing documentation
- Changing document content
- After database reset
- First time setup

### ❌ You DON'T need to reload when:
- Just restarting the application
- Documents are already in Pinecone
- No document changes were made
- Just updating code (not docs)

---

## How It Works

### With Pinecone (Recommended)

```
Documents in docs/ folder
    ↓
POST /documents/reload
    ↓
Extract text → Chunk → Embed (OpenAI)
    ↓
Store in Pinecone (persistent)
    ↓
Future queries use Pinecone (NO re-embedding needed)
```

**Benefits:**
- ✅ Documents persist across restarts
- ✅ No re-embedding on every startup
- ✅ Shared across multiple app instances
- ✅ Fast vector search

### Without Pinecone (In-Memory)

```
Documents in docs/ folder
    ↓
POST /documents/reload
    ↓
Extract text → Chunk (no embedding)
    ↓
Store in RAM
    ↓
Lost on restart (need to reload)
```

**Note:** In-memory is a fallback. Use Pinecone for production.

---

## Check Document Status

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "in_memory_docs_count": 150,
  "document_count": 150,
  "version": "2.0.0"
}
```

### Root Endpoint
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "running",
  "message": "AI Helpdesk Running",
  "in_memory_docs": 150,
  "version": "2.0.0"
}
```

---

## Troubleshooting

### "No documentation has been loaded"

**Problem:** Getting this message in chatbot responses

**Solution:**
1. Check if documents are loaded:
   ```bash
   curl http://localhost:8000/health
   ```
2. If `document_count` is 0, reload documents:
   ```bash
   curl -X POST "http://localhost:8000/documents/reload" -F "tenant_id=default"
   ```

### "Documents not found in Pinecone"

**Problem:** Pinecone index is empty

**Solution:**
1. Verify Pinecone configuration in `.env`:
   ```
   PINECONE_API_KEY=your-key
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=erp-helpdesk
   ```

2. Reload documents:
   ```bash
   curl -X POST "http://localhost:8000/documents/reload" -F "tenant_id=default"
   ```

### "OpenAI API error during embedding"

**Problem:** Embedding fails

**Solution:**
1. Check OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

2. Verify API key is valid:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

---

## Best Practices

### 1. Initial Setup
```bash
# One-time setup after first install
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# In another terminal, load documents
curl -X POST "http://localhost:8000/documents/reload" -F "tenant_id=default"
curl -X POST "http://localhost:8000/documents/reload-markdown" -F "tenant_id=default"
```

### 2. Adding New Documents
```bash
# Add file to docs/ folder
cp new_document.pdf docs/

# Reload
curl -X POST "http://localhost:8000/documents/reload" -F "tenant_id=default"
```

### 3. Production Deployment
- Use Pinecone (not in-memory)
- Load documents ONCE after deployment
- Set up document update workflow
- Monitor document count in health checks

---

## Summary

| Action | Command | What it does |
|--------|---------|--------------|
| Upload single file | `POST /documents/upload` | Upload one PDF/DOCX/XLSX/TXT file |
| Reload all docs | `POST /documents/reload` | ✅ **Loads ALL files including .md** |
| Reload markdown only | `POST /documents/reload-markdown` | Load only .md files (optional) |
| Check status | `GET /health` | Check document count |
| API docs | http://localhost:8000/docs | Interactive API documentation |

**Important:** 
- ✅ `/documents/reload` now automatically loads **markdown files** too!
- ✅ Documents persist in Pinecone - you only need to load them ONCE! 🎉
- ✅ Markdown uses structure-aware chunking automatically

