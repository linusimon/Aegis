"""Pytest unit tests for What-If scenario simulation API (/api/whatif)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_whatif_default_simulation(client):
    payload = {
        "workload_pct": 25.0,
        "duration_days": 30,
        "capacity_delta_nodes": 0,
        "arm_migration": False
    }
    response = client.post("/api/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Workload +25.0%" in data["scenario_name"]
    assert "projected_cost" in data
    assert "current_cost" in data
    assert "savings_pct" in data
    assert "target_met" in data

def test_api_whatif_arm_migration_savings(client):
    payload = {
        "workload_pct": 0.0,
        "duration_days": 30,
        "capacity_delta_nodes": -1,
        "arm_migration": True
    }
    response = client.post("/api/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_met"] is True
