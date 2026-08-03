"""Pytest Test Suite for Milestone 7: Scenario Simulation Agent ("What-If" Stress Tester)."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.scenario_simulator import simulate_what_if_scenario
from app.agents.scenario_agent import ScenarioSimulationAgent


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Scenario Simulation Engine Unit Tests
# -------------------------------------------------------------------
def test_scenario_simulator_traffic_surge():
    baseline_forecasts = [
        {
            "node_id": "node-01",
            "points": [
                {"timestamp": "2026-08-05T10:00:00Z", "predicted_cpu_pct": 50.0, "predicted_memory_pct": 60.0, "predicted_storage_gb": 200.0}
            ]
        }
    ]
    baseline_risk = {"cluster_health_score": 90.0}
    baseline_finops = {"total_current_monthly_cost": 1000.0}

    # Simulate +50% traffic multiplier
    res = simulate_what_if_scenario(
        baseline_forecasts, baseline_risk, baseline_finops,
        traffic_multiplier=1.5, capacity_delta_nodes=0, arm_migration=False
    )

    assert res["parameters"]["traffic_multiplier"] == 1.5
    sim_pts = res["simulated_forecasts"][0]["points"]
    assert sim_pts[0]["predicted_cpu_pct"] == 75.0  # 50.0 * 1.5


def test_scenario_simulator_arm_migration_cost_savings():
    baseline_forecasts = [{"node_id": "node-01", "points": []}]
    baseline_risk = {"cluster_health_score": 90.0}
    baseline_finops = {"total_current_monthly_cost": 1000.0}

    # Simulate ARM migration
    res = simulate_what_if_scenario(
        baseline_forecasts, baseline_risk, baseline_finops,
        traffic_multiplier=1.0, capacity_delta_nodes=0, arm_migration=True
    )

    assert res["simulated"]["monthly_cost"] < 1000.0
    assert res["impact_deltas"]["monthly_cost_delta"] < 0.0


# -------------------------------------------------------------------
# 2. Scenario Agent & MCP Integration Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_agent_execution():
    agent = ScenarioSimulationAgent()
    res = await agent.execute_simulation(traffic_multiplier=1.75, capacity_delta_nodes=-1, arm_migration=True)
    assert res["parameters"]["traffic_multiplier"] == 1.75
    assert "impact_deltas" in res


# -------------------------------------------------------------------
# 3. FastAPI Endpoint Tests
# -------------------------------------------------------------------
def test_api_simulate_endpoint(client):
    payload = {
        "traffic_multiplier": 1.5,
        "capacity_delta_nodes": -1,
        "arm_migration": True
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "simulation" in data
