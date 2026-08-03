"""Pytest Test Suite for Milestone 5: AI Time-Series Forecasting Agent (Target >= 80% Accuracy)."""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.services.forecasting_engine import generate_node_forecast, calculate_mape_and_rmse
from app.services.synthetic_generator import generate_synthetic_metrics, SyntheticMetricConfig
from app.agents.forecast_agent import ForecastingAgent


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Forecasting Engine Unit Tests
# -------------------------------------------------------------------
def test_mape_and_rmse_calculation():
    import numpy as np
    actuals = np.array([50.0, 55.0, 60.0, 65.0, 70.0])
    preds = np.array([49.0, 56.0, 59.0, 66.0, 69.0])

    mape, rmse, accuracy = calculate_mape_and_rmse(actuals, preds)
    assert mape < 5.0
    assert rmse < 2.0
    assert accuracy >= 80.0


def test_generate_node_forecast_30_days():
    config = SyntheticMetricConfig(num_nodes=1, duration_days=14, interval_minutes=60, trend="linear_up")
    batch = generate_synthetic_metrics(config)
    records = [r.model_dump(mode="json") for r in batch.records]

    result = generate_node_forecast(records, node_id="node-prod-01", horizon_days=30)
    assert result.node_id == "node-prod-01"
    assert result.horizon_days == 30
    assert len(result.points) == 30
    assert result.accuracy_pct >= 80.0
    assert result.target_accuracy_met is True

    # Test confidence bounds consistency
    for pt in result.points:
        assert pt.lower_bound_cpu <= pt.predicted_cpu_pct <= pt.upper_bound_cpu
        assert pt.lower_bound_memory <= pt.predicted_memory_pct <= pt.upper_bound_memory


# -------------------------------------------------------------------
# 2. Forecasting Agent MCP Integration Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_forecasting_agent_mcp_workflow():
    agent = ForecastingAgent()
    res = await agent.execute_forecast_for_node("node-prod-01", horizon_days=7)
    assert res.node_id == "node-prod-01"
    assert res.horizon_days == 7
    assert res.target_accuracy_met is True


# -------------------------------------------------------------------
# 3. FastAPI Endpoint Tests
# -------------------------------------------------------------------
def test_api_trigger_forecast_endpoint(client):
    response = client.post("/api/forecast?horizon_days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_nodes_forecasted"] >= 1
    assert "forecasts" in data


def test_api_get_node_forecast_endpoint(client):
    response = client.get("/api/forecast/node-prod-01")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "forecast" in data
