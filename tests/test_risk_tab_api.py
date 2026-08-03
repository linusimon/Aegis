"""Pytest unit tests for Risk & Reliability Operations Center API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_risk_assessment_endpoint_default(client):
    response = client.get("/api/v1/advisory/risk-assessment")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "risk_assessment" in data

def test_risk_assessment_custom_sla_limits(client):
    response = client.get("/api/v1/advisory/risk-assessment?cpu_limit=75.0&mem_limit=80.0")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    summary = data["risk_assessment"]
    assert "cluster_health_score" in summary
    assert "node_assessments" in summary
