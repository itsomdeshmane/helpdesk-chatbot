"""
Integration tests for Smart Chat V2 Router

Tests the full request/response flow through the router.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
class TestSmartChatV2Integration:
    """Integration tests for V2 router"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test V2 health check endpoint"""
        response = client.get("/chat/smart/v2/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["architecture"] == "SOLID V2"
    
    @pytest.mark.asyncio
    async def test_query_endpoint_structure(self, client):
        """Test V2 query endpoint structure (without actual processing)"""
        # This test verifies the endpoint exists and validates input
        # Actual processing requires mocking or test environment
        
        # Test with missing fields (should fail validation)
        response = client.post("/chat/smart/v2/query", json={})
        
        # Should return validation error (422)
        assert response.status_code == 422
    
    def test_query_endpoint_validation(self, client):
        """Test request validation"""
        # Test with invalid data
        response = client.post(
            "/chat/smart/v2/query",
            json={
                "query": "",  # Empty query (invalid)
                "source": "auto",
                "tenant_id": "test"
            }
        )
        
        # Should fail validation
        assert response.status_code == 422
        
        # Test with query too long
        response = client.post(
            "/chat/smart/v2/query",
            json={
                "query": "x" * 3000,  # Exceeds max length
                "source": "auto",
                "tenant_id": "test"
            }
        )
        
        # Should fail validation
        assert response.status_code == 422

