# 🧪 Testing Guide for SOLID Architecture

**Purpose**: Comprehensive testing guide for the refactored backend  
**Status**: Test suite ready to use

---

## 📋 Overview

The SOLID architecture includes a comprehensive test suite:
- ✅ **Unit tests**: Test individual components in isolation
- ✅ **Integration tests**: Test component interactions
- ✅ **Mocking**: Easy to mock dependencies (DI makes this simple)
- ✅ **Fixtures**: Reusable test data and mocks

---

## 🚀 Quick Start

### **Run All Tests**

```bash
cd backend

# Option 1: Using pytest directly
pytest -v tests/

# Option 2: Using test runner script
python run_tests.py --mode all
```

### **Run Specific Test Types**

```bash
# Unit tests only (fast)
python run_tests.py --mode unit

# Integration tests only
python run_tests.py --mode integration

# Quick smoke tests
python run_tests.py --mode quick
```

### **Run Specific Test File**

```bash
pytest -v tests/unit/test_chat_orchestrator.py
```

### **Run Specific Test Function**

```bash
pytest -v tests/unit/test_chat_orchestrator.py::TestChatOrchestrator::test_init
```

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and config
│
├── unit/                            # Unit tests (isolated)
│   ├── __init__.py
│   ├── test_chat_orchestrator.py   # ChatOrchestrator tests
│   ├── test_openai_provider.py     # OpenAI provider tests
│   └── test_vector_data_source.py  # Vector data source tests
│
└── integration/                     # Integration tests
    ├── __init__.py
    ├── test_router_integration.py  # Router integration tests
    └── test_di_container.py        # DI container tests
```

---

## 🧪 Writing Tests

### **Unit Test Example**

```python
import pytest
from unittest.mock import AsyncMock
from application.services.chat_orchestrator import ChatOrchestrator


@pytest.mark.unit
class TestChatOrchestrator:
    """Test suite for ChatOrchestrator"""
    
    def test_init(
        self,
        mock_llm_provider,
        mock_embedding_service
    ):
        """Test initialization"""
        orchestrator = ChatOrchestrator(
            data_sources=[],
            llm_provider=mock_llm_provider,
            embedding_service=mock_embedding_service,
            # ... other dependencies
        )
        
        assert orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_process_query(
        self,
        sample_query,
        mock_llm_provider
    ):
        """Test query processing"""
        # Arrange
        orchestrator = ChatOrchestrator(...)
        
        # Act
        response = await orchestrator.process_query(sample_query)
        
        # Assert
        assert response.success is True
```

### **Integration Test Example**

```python
import pytest
from core.container import AppContainer


@pytest.mark.integration
class TestDIContainer:
    """Test DI container integration"""
    
    def test_container_wiring(self):
        """Test all dependencies wire correctly"""
        container = AppContainer()
        
        # Get services
        orchestrator = container.chat_orchestrator()
        llm = container.llm_provider()
        
        # Verify wiring
        assert orchestrator.llm_provider is llm
```

---

## 🎭 Using Fixtures

### **Built-in Fixtures**

All fixtures are defined in `tests/conftest.py`:

#### **Mock Services**
```python
def test_my_service(
    mock_llm_provider,      # Mock LLM provider
    mock_embedding_service, # Mock embeddings
    mock_vector_store,      # Mock vector DB
    mock_database_connection  # Mock database
):
    # Use mocks in test
    pass
```

#### **Sample Data**
```python
def test_with_data(
    sample_query,              # Sample Query object
    sample_query_context,      # Sample QueryContext
    sample_chat_response,      # Sample ChatResponse
    sample_documents          # Sample documents list
):
    # Use sample data
    pass
```

#### **Configuration**
```python
def test_config(
    mock_db_config,      # Mock DB config
    mock_openai_config,  # Mock OpenAI config
    mock_settings        # Mock Settings
):
    # Use mock configs
    pass
```

### **Custom Fixtures**

Add fixtures to `conftest.py`:

```python
@pytest.fixture
def my_custom_fixture():
    """My custom fixture"""
    return {"key": "value"}
```

---

## 🎯 Test Markers

Use markers to categorize tests:

### **Available Markers**

```python
@pytest.mark.unit             # Unit test
@pytest.mark.integration      # Integration test
@pytest.mark.slow             # Slow test
@pytest.mark.requires_db      # Requires database
@pytest.mark.requires_openai  # Requires OpenAI API
@pytest.mark.requires_pinecone  # Requires Pinecone
```

### **Run Tests by Marker**

```bash
# Run only unit tests
pytest -v -m unit

# Run tests that DON'T require database
pytest -v -m "not requires_db"

# Run unit tests that don't require external services
pytest -v -m "unit and not requires_openai"
```

---

## 🔧 Mocking with Dependency Injection

### **Why Mocking is Easy**

Dependency injection makes mocking trivial:

```python
# WITHOUT DI (hard to mock)
class OldService:
    def __init__(self):
        self.llm = OpenAI(api_key=GLOBAL_KEY)  # Hard-coded!
        
# WITH DI (easy to mock)
class NewService:
    def __init__(self, llm_provider: ILLMProvider):
        self.llm = llm_provider  # Injected! Can be real or mock
```

### **Mock Example**

```python
from unittest.mock import AsyncMock

def test_service():
    # Create mock
    mock_llm = AsyncMock(spec=ILLMProvider)
    mock_llm.generate_completion.return_value = "Test response"
    
    # Inject mock
    service = MyService(llm_provider=mock_llm)
    
    # Test
    result = await service.process()
    
    # Verify mock was called
    mock_llm.generate_completion.assert_called_once()
```

---

## 📊 Test Coverage

### **Generate Coverage Report**

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term tests/

# View HTML report
# Open htmlcov/index.html in browser
```

### **Target Coverage**

- ✅ **Core interfaces**: 100% (easy, just contracts)
- ✅ **Application layer**: 80%+ (business logic)
- ✅ **Infrastructure**: 60%+ (hard to test without real services)
- ✅ **Routers**: 70%+ (integration tests)

---

## 🐛 Debugging Tests

### **Run with Debugger**

```bash
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run test
pytest -v tests/unit/test_chat_orchestrator.py -s
```

### **Print Debug Info**

```bash
# Show print statements
pytest -v -s tests/

# Show debug logs
pytest -v --log-cli-level=DEBUG tests/
```

### **Stop on First Failure**

```bash
pytest -v -x tests/
```

---

## ✅ Test Checklist

Before committing code, ensure:

- [ ] ✅ All unit tests pass
- [ ] ✅ All integration tests pass
- [ ] ✅ New features have tests
- [ ] ✅ Coverage doesn't decrease
- [ ] ✅ No skipped tests (unless intentional)
- [ ] ✅ Mock external services
- [ ] ✅ Tests run quickly (< 30 seconds for unit tests)

---

## 📈 Continuous Integration

### **GitHub Actions Example**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements-refactor.txt
          pip install pytest pytest-asyncio pytest-mock
      
      - name: Run tests
        run: pytest -v tests/
```

---

## 🎓 Best Practices

### **1. Test Behavior, Not Implementation**

```python
# ❌ BAD: Tests internal implementation
def test_bad():
    orchestrator = ChatOrchestrator(...)
    assert orchestrator._internal_cache == {}  # Implementation detail

# ✅ GOOD: Tests behavior
def test_good():
    orchestrator = ChatOrchestrator(...)
    response = await orchestrator.process_query(query)
    assert response.success is True  # Public behavior
```

### **2. Use AAA Pattern**

```python
def test_my_function():
    # Arrange: Set up test data
    query = Query(text="test")
    
    # Act: Execute function
    result = await my_function(query)
    
    # Assert: Verify result
    assert result is not None
```

### **3. One Assert Per Test (Usually)**

```python
# ❌ BAD: Multiple unrelated asserts
def test_bad():
    assert service.method1() == "a"
    assert service.method2() == "b"
    assert service.method3() == "c"

# ✅ GOOD: One concept per test
def test_method1():
    assert service.method1() == "a"
    
def test_method2():
    assert service.method2() == "b"
```

### **4. Use Descriptive Test Names**

```python
# ❌ BAD
def test_1():
    pass

# ✅ GOOD
def test_query_processing_returns_success_response():
    pass
```

### **5. Mock External Services**

```python
# ✅ ALWAYS mock external APIs
@patch('openai.ChatCompletion.create')
async def test_llm_call(mock_openai):
    mock_openai.return_value = {"choices": [...]}
    # Test...
```

---

## 🆘 Troubleshooting

### **Issue: "Import Error"**

```bash
# Solution: Ensure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"

# Or use pytest's automatic path discovery
pytest -v tests/
```

### **Issue: "Async Tests Don't Run"**

```bash
# Solution: Install pytest-asyncio
pip install pytest-asyncio

# Ensure pytest.ini has:
# asyncio_mode = auto
```

### **Issue: "Mocks Not Working"**

```python
# Solution: Use spec parameter
mock = AsyncMock(spec=ILLMProvider)  # ✅ Type-safe mock
```

### **Issue: "Tests Pass Locally, Fail in CI"**

```bash
# Possible causes:
# 1. Environment variables not set
# 2. External services required
# 3. Database not available

# Solution: Mark tests appropriately
@pytest.mark.requires_db  # Skip if no DB
@pytest.mark.requires_openai  # Skip if no API key
```

---

## 📚 Additional Resources

- **pytest docs**: https://docs.pytest.org/
- **pytest-asyncio docs**: https://pytest-asyncio.readthedocs.io/
- **unittest.mock docs**: https://docs.python.org/3/library/unittest.mock.html
- **Testing best practices**: https://testdriven.io/

---

## 🎉 Summary

The test suite provides:
- ✅ Comprehensive coverage
- ✅ Easy mocking (thanks to DI)
- ✅ Fast unit tests
- ✅ Integration tests
- ✅ Clear documentation
- ✅ CI/CD ready

**Write tests, run tests, ship with confidence!** 🚀

---

**Last Updated**: December 17, 2025  
**Status**: Test suite complete and ready

