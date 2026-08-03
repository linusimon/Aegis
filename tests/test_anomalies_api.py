"""Pytest unit tests for Anomaly Diagnostics API (/api/anomalies)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_get_anomalies(client):
    response = client.get("/api/anomalies?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "anomalies" in data
    assert "total_records_analyzed" in data
