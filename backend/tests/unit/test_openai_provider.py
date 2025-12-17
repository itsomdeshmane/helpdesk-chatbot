"""
Unit tests for OpenAI Provider

Tests the OpenAI LLM provider implementation.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from infrastructure.llm.openai_provider import OpenAIProvider


@pytest.mark.unit
class TestOpenAIProvider:
    """Test suite for OpenAI Provider"""
    
    def test_init(self):
        """Test provider initialization"""
        provider = OpenAIProvider(
            api_key="test_key",
            model="gpt-4",
            max_tokens=500,
            temperature=0.7
        )
        
        assert provider is not None
        assert provider.get_model() == "gpt-4"
        assert provider.get_provider_name() == "openai"
    
    @pytest.mark.asyncio
    async def test_count_tokens(self):
        """Test token counting"""
        provider = OpenAIProvider(api_key="test_key", model="gpt-4")
        
        # Test simple text
        count = await provider.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)
        
        # Test longer text
        long_text = "This is a longer text " * 50
        long_count = await provider.count_tokens(long_text)
        assert long_count > count
    
    @pytest.mark.asyncio
    @pytest.mark.requires_openai
    @patch('openai.AsyncOpenAI')
    async def test_generate_completion(self, mock_openai_class):
        """Test completion generation (mocked)"""
        # Setup mock
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client
        
        # Create provider
        provider = OpenAIProvider(api_key="test_key", model="gpt-4")
        provider.client = mock_client
        
        # Execute
        messages = [{"role": "user", "content": "Test"}]
        response = await provider.generate_completion(messages)
        
        # Assert
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_get_max_tokens(self):
        """Test get_max_tokens method"""
        provider = OpenAIProvider(
            api_key="test_key",
            model="gpt-4",
            max_tokens=1000
        )
        
        assert provider.get_max_tokens() == 1000

