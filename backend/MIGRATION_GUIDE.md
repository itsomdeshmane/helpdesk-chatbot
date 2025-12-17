# 🔄 Migration Guide: Global State → Dependency Injection

**Purpose**: Guide for migrating legacy code from global state to SOLID architecture  
**Status**: Backend uses new architecture, legacy code can coexist safely

---

## 📋 Overview

The new SOLID architecture eliminates global state and singletons in favor of dependency injection. However, for backward compatibility, a **legacy bridge** allows old and new code to coexist during migration.

### **Current State**:
- ✅ New code uses DI (SOLID architecture)
- ✅ Old code can still use global state
- ✅ Bridge provides compatibility layer
- ✅ Both systems work side-by-side

### **Migration Strategy**:
- 🎯 Incremental migration (not big-bang)
- 🎯 One component at a time
- 🎯 No breaking changes
- 🎯 Easy rollback if needed

---

## 🔍 Identifying Global State

### **Common Patterns to Migrate**:

#### **1. Global Variables**
```python
# ❌ OLD (Global state)
from llm.rag import in_memory_docs

docs = in_memory_docs.get("tenant_id", [])
```

#### **2. Singleton Instances**
```python
# ❌ OLD (Singleton)
from database.db_manager import db_manager

results = db_manager.execute_query("SELECT ...")
```

#### **3. Direct Module Imports**
```python
# ❌ OLD (Direct import)
from config import GPT_MODEL, OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY
response = openai.ChatCompletion.create(model=GPT_MODEL, ...)
```

---

## ✅ Migration Patterns

### **Pattern 1: Using Legacy Bridge (Quick Migration)**

The **legacy bridge** provides DI-managed instances to legacy code.

#### **Example: LLM Provider**

```python
# ❌ OLD
from config import GPT_MODEL
import openai

def generate_response(prompt):
    return openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

# ✅ NEW (using legacy bridge)
from utils.legacy_bridge import get_llm_provider

async def generate_response(prompt):
    llm = get_llm_provider()
    return await llm.generate_completion(
        messages=[{"role": "user", "content": prompt}]
    )
```

**Benefits**:
- ✅ Uses DI-managed instance
- ✅ Minimal code changes
- ✅ Works with both old and new code
- ✅ Easy to refactor further later

---

#### **Example: Vector Store**

```python
# ❌ OLD
from llm.rag import in_memory_docs

def get_docs(tenant_id):
    return in_memory_docs.get(tenant_id, [])

# ✅ NEW (using legacy bridge)
from utils.legacy_bridge import get_vector_store

async def get_docs(tenant_id):
    store = get_vector_store()
    # store is now a proper IVectorStore implementation
    return await store.get_stats()  # or other methods
```

---

#### **Example: Database**

```python
# ❌ OLD
from database.db_manager import db_manager

def query_data(sql):
    return db_manager.execute_query(sql)

# ✅ NEW (using legacy bridge)
from utils.legacy_bridge import get_system_database

async def query_data(sql):
    db = get_system_database()
    return await db.execute_query(sql)
```

---

### **Pattern 2: Full Dependency Injection (Best Practice)**

For new code or complete refactoring, use full DI.

#### **Example: Service Class**

```python
# ❌ OLD
from config import OPENAI_API_KEY
from database.db_manager import db_manager
import openai

class MyService:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.db = db_manager  # Global singleton
        
    def process(self, query):
        # Use global state
        response = openai.ChatCompletion.create(...)
        self.db.save_result(...)

# ✅ NEW (full DI)
from core.interfaces.llm_provider import ILLMProvider
from core.interfaces.database import IDatabaseConnection

class MyService:
    def __init__(
        self,
        llm_provider: ILLMProvider,
        database: IDatabaseConnection
    ):
        self.llm = llm_provider  # Injected dependency
        self.db = database        # Injected dependency
        
    async def process(self, query):
        # Use injected dependencies
        response = await self.llm.generate_completion(...)
        await self.db.execute_query(...)
```

**Benefits**:
- ✅ Fully testable (can mock dependencies)
- ✅ No global state
- ✅ Follows SOLID principles
- ✅ Easy to swap implementations

---

## 🛠️ Step-by-Step Migration

### **Step 1: Identify Dependencies**

List all global state your code uses:

```python
# Example analysis
# File: my_module.py
# Dependencies:
# - from llm.rag import in_memory_docs (GLOBAL)
# - from database.db_manager import db_manager (SINGLETON)
# - from config import OPENAI_API_KEY (GLOBAL CONFIG)
```

---

### **Step 2: Choose Migration Approach**

**Quick Migration** (1-5 minutes per file):
- Use legacy bridge
- Minimal code changes
- Good for: low-priority files, quick wins

**Full Migration** (10-30 minutes per file):
- Use full DI
- Refactor to use interfaces
- Good for: core logic, new features

---

### **Step 3: Implement Changes**

#### **Quick Migration Example**:

```python
# Before
from llm.rag import generate_rag_response

def handle_query(query):
    return generate_rag_response(query)

# After (5 minutes)
from utils.legacy_bridge import get_chat_orchestrator
from core.models.query import Query

async def handle_query(query_text):
    orchestrator = get_chat_orchestrator()
    query = Query(text=query_text)
    response = await orchestrator.process_query(
        query=query,
        tenant_id="default"
    )
    return response.message
```

#### **Full Migration Example**:

```python
# Before
class DocumentProcessor:
    def __init__(self):
        from llm.rag import in_memory_docs
        self.docs = in_memory_docs
    
    def process(self):
        # ...

# After (20 minutes)
from core.interfaces.vector_store import IVectorStore

class DocumentProcessor:
    def __init__(self, vector_store: IVectorStore):
        self.vector_store = vector_store  # Injected
    
    async def process(self):
        # Use self.vector_store instead
```

---

### **Step 4: Test**

```python
# Test with legacy bridge
from utils.legacy_bridge import is_new_architecture_available

def test_my_function():
    assert is_new_architecture_available(), "DI not ready"
    result = await my_function()
    assert result is not None
```

---

### **Step 5: Update Container (if full migration)**

If you created a new service with DI, register it:

```python
# core/container.py

# Add to container
my_service = providers.Singleton(
    MyService,
    llm_provider=llm_provider,
    database=system_database
)
```

---

## 📊 Migration Priority

### **High Priority** (Migrate First):
1. ✅ **Routers** - Already done (`smart_chat_v2.py`)
2. ⏳ **Core services** - Use legacy bridge or full DI
3. ⏳ **Business logic** - Gradually migrate to DI

### **Medium Priority**:
4. ⏳ **Utilities** - Use legacy bridge
5. ⏳ **Background jobs** - Use legacy bridge
6. ⏳ **Scripts** - Use legacy bridge

### **Low Priority** (Can wait):
7. ⏳ **Old routers** - Keep as-is (will be removed eventually)
8. ⏳ **Test files** - Migrate when touched
9. ⏳ **One-off scripts** - No migration needed

---

## 🔧 Legacy Bridge API Reference

### **Available Functions**:

```python
from utils.legacy_bridge import (
    get_llm_provider,        # Get LLM provider
    get_embedding_service,   # Get embedding service
    get_vector_store,        # Get vector store
    get_system_database,     # Get system database
    get_chat_orchestrator,   # Get chat orchestrator
    is_new_architecture_available,  # Check if DI ready
)

# Check if DI is available
if is_new_architecture_available():
    llm = get_llm_provider()
    # Use llm...
else:
    # Fallback to old code
    pass
```

### **Usage in Legacy Code**:

```python
# Option 1: Direct replacement
# Old: from database.db_manager import db_manager
# New:
from utils.legacy_bridge import get_system_database
db = get_system_database()

# Option 2: Conditional usage
from utils.legacy_bridge import (
    get_llm_provider,
    is_new_architecture_available
)

if is_new_architecture_available():
    llm = get_llm_provider()  # Use new DI
else:
    import openai
    # Use old code
```

---

## ⚠️ Important Warnings

### **DO NOT**:
- ❌ Don't mix global state and DI in same function
- ❌ Don't create new global variables
- ❌ Don't add new singletons
- ❌ Don't modify legacy code if not needed

### **DO**:
- ✅ Use legacy bridge for quick wins
- ✅ Use full DI for new features
- ✅ Test after migration
- ✅ Update one component at a time
- ✅ Keep backward compatibility

---

## 🧪 Testing During Migration

### **Unit Tests**:

```python
# Test with DI
from core.container import AppContainer

def test_my_service():
    # Create container
    container = AppContainer()
    
    # Get service
    service = container.my_service()
    
    # Test
    result = await service.process()
    assert result is not None
```

### **Integration Tests**:

```python
# Test with legacy bridge
from utils.legacy_bridge import get_chat_orchestrator

async def test_integration():
    orchestrator = get_chat_orchestrator()
    response = await orchestrator.process_query(...)
    assert response.success
```

---

## 📈 Migration Progress Tracking

### **Checklist**:

#### **Core Components**:
- [x] Routers (smart_chat_v2.py) ✅
- [ ] RAG service (`llm/rag.py`)
- [ ] Database query service (`llm/database_query_service.py`)
- [ ] DB Manager (`database/db_manager.py`)

#### **Secondary Components**:
- [ ] Other routers (analytics, feedback, etc.)
- [ ] Utility functions
- [ ] Background jobs

#### **Frontend**:
- [ ] API service layer
- [ ] React components
- [ ] State management

---

## 🎯 Success Criteria

### **Migration Complete When**:
- ✅ No new global variables created
- ✅ All new code uses DI
- ✅ Legacy code uses legacy bridge (if needed)
- ✅ All tests pass
- ✅ No breaking changes

---

## 💡 Tips & Best Practices

### **1. Start Small**:
Pick one small file, migrate it, test it, commit it.

### **2. Use TypeScript-style Thinking**:
Think of interfaces as TypeScript interfaces - they define contracts.

### **3. Test First**:
Write tests before migrating to ensure behavior doesn't change.

### **4. Document Changes**:
Add comments explaining the migration.

```python
# MIGRATION NOTE: Migrated from global db_manager to DI
# Old: from database.db_manager import db_manager
# New: Injected IDatabaseConnection
```

### **5. Keep Legacy Code Working**:
Don't break old code during migration.

---

## 🆘 Troubleshooting

### **Issue: "DI container not set"**

```python
# Solution: Check app.py initializes container
from core.container import AppContainer
container = AppContainer()
container.wire(...)
```

### **Issue: "Legacy bridge returns None"**

```python
# Solution: Ensure container is wired before accessing
from utils.legacy_bridge import is_new_architecture_available

if not is_new_architecture_available():
    raise RuntimeError("DI not initialized")
```

### **Issue: "Tests fail after migration"**

```python
# Solution: Mock dependencies in tests
from unittest.mock import Mock

def test_service():
    mock_llm = Mock(spec=ILLMProvider)
    service = MyService(mock_llm)
    # Test...
```

---

## 📚 Additional Resources

- `DEPLOYMENT_GUIDE.md` - How to deploy SOLID architecture
- `core/README.md` - Understanding the new architecture
- `REFACTORING_COMPLETE_SUMMARY.md` - What changed and why

---

## ✅ Conclusion

The legacy bridge makes migration safe and incremental:
- ✅ Old code keeps working
- ✅ New code uses best practices
- ✅ No big-bang refactor needed
- ✅ Easy to test and validate

**Migrate at your own pace. Both systems work together!**

---

**Last Updated**: December 17, 2025  
**Status**: Legacy bridge active and ready for use

