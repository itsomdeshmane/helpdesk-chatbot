# Core Module - SOLID Architecture Foundation

## Overview

The `core` module contains the foundation of the SOLID-compliant architecture:
- **Interfaces**: Abstractions following DIP (Dependency Inversion Principle)
- **Models**: Domain models following DDD (Domain-Driven Design)
- **Container**: Dependency Injection configuration
- **Config**: Enhanced configuration management

## Structure

```
core/
├── __init__.py
├── README.md (this file)
├── config.py          # Enhanced configuration
├── container.py       # DI container
├── interfaces/        # Abstractions (SOLID)
│   ├── __init__.py
│   ├── data_source.py
│   ├── llm_provider.py
│   ├── embedding_service.py
│   ├── database.py
│   ├── vector_store.py
│   └── repository.py
└── models/            # Domain models
    ├── __init__.py
    ├── query.py
    ├── response.py
    └── conversation.py
```

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- Each interface has ONE responsibility
- Each model represents ONE domain concept
- Configuration is split into separate classes by concern

### Open-Closed Principle (OCP)
- Interfaces are open for extension (new implementations)
- Interfaces are closed for modification
- Example: Add new data source without changing IDataSource

### Liskov Substitution Principle (LSP)
- All implementations of an interface are substitutable
- Example: OpenAIProvider and AnthropicProvider both implement ILLMProvider

### Interface Segregation Principle (ISP)
- Interfaces contain only essential methods
- No fat interfaces forcing unnecessary implementations

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions (interfaces)
- Low-level modules implement abstractions
- DI container wires everything together

## Usage

### 1. Using Interfaces

```python
from core.interfaces import ILLMProvider, IDataSource
from core.models import Query, ChatResponse

# High-level code depends on abstractions
async def process_query(
    query: Query,
    data_source: IDataSource,  # ← Interface, not concrete class
    llm: ILLMProvider          # ← Interface, not concrete class
) -> ChatResponse:
    # Use any implementation of IDataSource and ILLMProvider
    results = await data_source.search(query, tenant_id="test")
    response = await llm.generate_completion([...])
    return ChatResponse(success=True, message=response, source="documents")
```

### 2. Using DI Container

```python
from core.container import container

# Initialize container
container.init_resources()

# Get services (automatically wired)
llm_provider = container.llm_provider()
chat_orchestrator = container.chat_orchestrator()

# Use services
response = await chat_orchestrator.process_query(query)
```

### 3. Using Domain Models

```python
from core.models import Query, QueryContext, ChatResponse

# Create a query
context = QueryContext(
    session_id="abc123",
    tenant_id="tenant_1",
    user_id="user_123"
)

query = Query(
    text="How do I create a work order?",
    source_preference="auto",
    context=context
)

# Create a response
response = ChatResponse.success_response(
    message="Here's how to create a work order...",
    source="documents",
    session_id=query.get_session_id()
)
```

## Configuration

Configuration is loaded from environment variables (.env file):

```env
# OpenAI
OPENAI_API_KEY=sk-...
GPT_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Pinecone
USE_PINECONE=true
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=erp-helpdesk

# System Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=...
MYSQL_DATABASE=helpdesk_db
```

Access configuration:

```python
from core.config import app_config

print(app_config.openai.model)
print(app_config.pinecone.use_pinecone)
print(app_config.system_database.host)
```

## Testing

The core module makes testing easy:

```python
import pytest
from unittest.mock import Mock
from core.interfaces import IDataSource
from core.models import Query, DataSourceResponse

# Mock a data source
@pytest.fixture
def mock_data_source():
    mock = Mock(spec=IDataSource)
    mock.search.return_value = DataSourceResponse(
        success=True,
        source_type="test",
        data=["result1", "result2"]
    )
    return mock

# Test using mock
async def test_process_query(mock_data_source):
    query = Query(text="test query")
    result = await mock_data_source.search(query, tenant_id="test")
    
    assert result.success is True
    assert result.source_type == "test"
```

## Extension Examples

### Adding a New Data Source

1. Implement the interface:

```python
from core.interfaces import IDataSource
from core.models import Query, DataSourceResponse

class ElasticsearchDataSource(IDataSource):
    async def can_handle(self, query: Query) -> bool:
        # Your logic
        return True
    
    async def search(self, query: Query, tenant_id: str, limit: int = 5):
        # Your Elasticsearch logic
        return DataSourceResponse(
            success=True,
            source_type="elasticsearch",
            data=results
        )
    
    def get_source_type(self) -> str:
        return "elasticsearch"
    
    async def health_check(self) -> bool:
        # Check Elasticsearch health
        return True
```

2. Register in DI container:

```python
# In core/container.py
elasticsearch_data_source = providers.Singleton(
    "infrastructure.data_sources.elasticsearch_data_source.ElasticsearchDataSource",
    # ... configuration
)
```

3. Done! No existing code needs to change ✅

### Adding a New LLM Provider

1. Implement the interface:

```python
from core.interfaces import ILLMProvider

class AnthropicProvider(ILLMProvider):
    async def generate_completion(self, messages, **kwargs):
        # Anthropic API call
        ...
    
    async def generate_streaming(self, messages, **kwargs):
        # Anthropic streaming
        ...
    
    def get_provider_name(self) -> str:
        return "anthropic"
    
    async def count_tokens(self, text: str) -> int:
        # Anthropic tokenization
        ...
```

2. Register and switch:

```python
# In core/container.py
llm_provider = providers.Singleton(
    "infrastructure.llm.anthropic_provider.AnthropicProvider",
    api_key=config.provided.anthropic.api_key
)
```

3. Application layer automatically uses the new provider ✅

## Next Steps

After completing the core module:
1. ✅ Core interfaces created
2. ✅ Domain models created
3. ✅ DI container configured
4. 🔄 Implement infrastructure layer (concrete implementations)
5. ⏳ Implement application layer (business logic)
6. ⏳ Refactor routers (thin controllers)

---

**Author**: Helpdesk Chatbot Team
**Version**: 2.0.0 (SOLID Refactoring)

