"""
Tests for health check endpoint.

Test ca:
- GET /health → 200 + {"status": "UP"}
- Response có X-Request-ID header
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from customer_analytics.main import app


@pytest.mark.asyncio
async def test_health_basic():
    """GET /health trả 200 và status UP."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_response_has_request_id():
    """Response có X-Request-ID header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

        assert "X-Request-ID" in response.headers
        # UUID format: 8-4-4-4-12 hex digits
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36
        assert request_id.count("-") == 4
