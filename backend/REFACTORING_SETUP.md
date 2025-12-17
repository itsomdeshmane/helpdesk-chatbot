# SOLID Refactoring - Setup Guide

Quick guide to set up and test the new SOLID architecture.

## 📋 Prerequisites

- Python 3.8+
- Existing helpdesk chatbot environment
- OpenAI API key configured

## 🚀 Installation

### Step 1: Install New Dependencies

```bash
cd backend
pip install -r requirements-refactor.txt
```

This installs:
- `dependency-injector` - DI container
- `pydantic>=2.0.0` - Data validation
- `pytest` + plugins - Testing framework
- `tiktoken` - Token counting

### Step 2: Verify Installation

```bash
python -c "from dependency_injector import containers; print('✅ DI container ready')"
python -c "from pydantic import BaseModel; print('✅ Pydantic ready')"
python -c "import tiktoken; print('✅ Tiktoken ready')"
```

## 🧪 Testing New Components

### Test 1: Configuration

```python
# test_config.py
from core.config import app_config

# Test configuration loading
print("OpenAI Model:", app_config.openai.model)
print("Pinecone Enabled:", app_config.pinecone.use_pinecone)
print("System DB:", app_config.system_database.database)

print("✅ Configuration loaded successfully!")
```

Run: `python test_config.py`

### Test 2: DI Container

```python
# test_container.py
from core.container import container

# Initialize container
container.init_resources()

# Get services
config = container.config()
print("✅ Config injected:", config.openai.model)

print("✅ DI Container working!")
```

Run: `python test_container.py`

### Test 3: OpenAI Provider

```python
# test_openai_provider.py
import asyncio
from infrastructure.llm.openai_provider import OpenAIProvider
from core.config import app_config

async def test():
    # Create provider
    provider = OpenAIProvider(
        api_key=app_config.openai.api_key,
        model=app_config.openai.model
    )
    
    # Test completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello SOLID!'"}
    ]
    
    response = await provider.generate_completion(messages, max_tokens=50)
    print("Response:", response)
    
    # Test token counting
    tokens = await provider.count_tokens("Hello world")
    print("Tokens:", tokens)
    
    print("✅ OpenAI Provider working!")

asyncio.run(test())
```

Run: `python test_openai_provider.py`

### Test 4: Embedding Service

```python
# test_embedding.py
import asyncio
from infrastructure.llm.openai_embedding import OpenAIEmbeddingService
from core.config import app_config

async def test():
    # Create service
    service = OpenAIEmbeddingService(
        api_key=app_config.openai.api_key,
        model=app_config.openai.embedding_model
    )
    
    # Test single embedding
    embedding = await service.create_embedding("Hello SOLID")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch embeddings
    texts = ["Hello", "World", "SOLID"]
    embeddings = await service.create_embeddings(texts)
    print(f"Batch embeddings: {len(embeddings)} vectors")
    
    print("✅ Embedding Service working!")

asyncio.run(test())
```

Run: `python test_embedding.py`

### Test 5: System Database

```python
# test_system_db.py
import asyncio
from infrastructure.databases.system_database import SystemDatabaseConnection
from core.config import app_config

async def test():
    # Create connection
    db = SystemDatabaseConnection(app_config.system_database)
    
    # Test health check
    healthy = await db.health_check()
    print(f"Database healthy: {healthy}")
    
    # Test query
    results = await db.execute_query("SELECT 1 as test")
    print(f"Query result: {results}")
    
    # Test schema
    schema = await db.get_schema()
    print(f"Tables found: {len(schema['tables'])}")
    for table in schema['tables'][:3]:
        print(f"  - {table['name']} ({len(table['columns'])} columns)")
    
    print("✅ System Database working!")

asyncio.run(test())
```

Run: `python test_system_db.py`

## 🔍 Verification Checklist

After installation, verify:

- [ ] ✅ Dependencies installed (`pip list | grep dependency-injector`)
- [ ] ✅ Configuration loads without errors
- [ ] ✅ DI container initializes
- [ ] ✅ OpenAI provider creates completions
- [ ] ✅ Embedding service generates embeddings
- [ ] ✅ System database connects and queries

## 🐛 Troubleshooting

### Issue: Import Error

```
ImportError: No module named 'dependency_injector'
```

**Solution**: Reinstall dependencies
```bash
pip install -r requirements-refactor.txt --force-reinstall
```

### Issue: Configuration Error

```
ValueError: OPENAI_API_KEY is required
```

**Solution**: Ensure `.env` file has required variables
```env
OPENAI_API_KEY=sk-...
MYSQL_HOST=localhost
MYSQL_DATABASE=helpdesk_db
```

### Issue: Database Connection Error

```
Error: Connection pool not initialized
```

**Solution**: Check MySQL is running and credentials are correct
```bash
mysql -u root -p -e "SHOW DATABASES;"
```

### Issue: Pydantic v2 Migration

If you see pydantic errors:
```bash
pip install "pydantic>=2.0.0" --upgrade
```

## 📊 Running Unit Tests

Once tests are created (Phase 2.8):

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=infrastructure

# Run specific test file
pytest tests/unit/test_openai_provider.py

# Run with verbose output
pytest -v
```

## 🔄 Integration with Existing Code

The new architecture is **fully backward compatible**:

- ✅ Existing `app.py` continues to work
- ✅ Existing routers continue to work
- ✅ No API contract changes
- ✅ Can use new and old code side-by-side

To use new components in existing code:

```python
# In any existing router or service
from core.container import container

# Get services via DI
llm_provider = container.llm_provider()
embedding_service = container.embedding_service()

# Use as before
response = await llm_provider.generate_completion(messages)
```

## 🚀 Next Steps

After verifying installation:

1. **Continue Infrastructure Implementation**
   - Complete remaining database classes
   - Implement vector stores
   - Implement data sources

2. **Create Application Layer**
   - Orchestrators
   - Services
   - Business logic

3. **Write Tests**
   - Unit tests for all classes
   - Integration tests
   - E2E tests

## 📖 Documentation

- **Core Module**: See `core/README.md`
- **Progress**: See `REFACTORING_PROGRESS.md`
- **Plan**: See Phase 2 plan document

## 🎯 Success Criteria

Installation is successful when:
- ✅ All test scripts run without errors
- ✅ Configuration loads correctly
- ✅ DI container initializes
- ✅ Can create instances of new classes
- ✅ Basic functionality works (LLM, embeddings, database)

---

**Last Updated**: December 17, 2025

