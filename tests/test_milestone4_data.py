"""Pytest Test Suite for Milestone 4: Data Processing Agent, Ingestion & Simulated Monitoring API."""
import json
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.metrics import SyntheticMetricConfig
from app.services.synthetic_generator import generate_synthetic_metrics
from app.services.data_parser import parse_metrics_file, anonymize_node_identifier
from app.agents.data_agent import DataProcessingAgent


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Synthetic Metric Generator Tests
# -------------------------------------------------------------------
def test_synthetic_generator_saas_growth_preset():
    config = SyntheticMetricConfig(num_nodes=3, duration_days=7, interval_minutes=60, trend="linear_up")
    batch = generate_synthetic_metrics(config)
    assert batch.total_records == (7 * 24 * 3)  # 7 days * 24 hrs * 3 nodes
    assert len(batch.records) > 0
    assert batch.source == "synthetic_generator"


def test_synthetic_generator_memory_leak_preset():
    config = SyntheticMetricConfig(num_nodes=2, duration_days=5, interval_minutes=60, memory_leak=True)
    batch = generate_synthetic_metrics(config)
    node_records = [r for r in batch.records if r.node_id == "node-prod-01"]
    assert len(node_records) > 0
    # Memory on leak node should increase over time
    first_mem = node_records[0].memory_utilization_pct
    last_mem = node_records[-1].memory_utilization_pct
    assert last_mem >= first_mem


# -------------------------------------------------------------------
# 2. Data Parser & Anonymizer Tests
# -------------------------------------------------------------------
def test_anonymize_node_identifier():
    ip_anon = anonymize_node_identifier("192.168.1.50")
    assert ip_anon.startswith("node-anon-")
    assert ip_anon != "192.168.1.50"


def test_parse_json_metrics_file():
    raw_json = json.dumps([
        {
            "timestamp": "2026-08-01T10:00:00Z",
            "host": "10.0.0.12",
            "cpu": 75.4,
            "memory": 82.1,
            "storage": 200.0
        }
    ]).encode("utf-8")

    batch = parse_metrics_file(raw_json, "test_metrics.json", anonymize=True)
    assert batch.total_records == 1
    assert batch.records[0].cpu_utilization_pct == 75.4
    assert batch.records[0].node_id.startswith("node-anon-")


# -------------------------------------------------------------------
# 3. Data Agent MCP Storage Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_data_agent_mcp_storage():
    agent = DataProcessingAgent()
    config = SyntheticMetricConfig(num_nodes=2, duration_days=1, interval_minutes=120)
    batch = generate_synthetic_metrics(config)

    result = await agent.process_and_store_batch(batch)
    assert result["status"] == "success"
    assert result["inserted_count"] == batch.total_records


# -------------------------------------------------------------------
# 4. FastAPI Endpoints & Simulated Monitoring API Tests
# -------------------------------------------------------------------
def test_api_generate_synthetic_endpoint(client):
    payload = {
        "num_nodes": 2,
        "duration_days": 1,
        "interval_minutes": 120,
        "trend": "linear_up"
    }
    response = client.post("/api/data/synthetic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["inserted_count"] > 0


def test_api_simulated_monitoring_metrics_endpoint(client):
    response = client.get("/api/v1/monitoring/metrics?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "metrics" in data


def test_api_simulated_prometheus_endpoint(client):
    response = client.get("/api/v1/monitoring/prometheus/query?query=cpu_utilization_pct")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["resultType"] == "vector"
