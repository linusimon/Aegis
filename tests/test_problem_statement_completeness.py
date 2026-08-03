"""Pytest Test Suite for Problem Statement Completeness (Anomaly Detection & User Feedback)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.anomaly_detector import detect_metric_anomalies


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Anomaly Detection Unit Tests
# -------------------------------------------------------------------
def test_detect_metric_anomalies_cpu_spike():
    records = [
        {"timestamp": "2026-08-01T10:00:00Z", "node_id": "node-01", "cpu_utilization_pct": 30.0, "memory_utilization_pct": 40.0},
        {"timestamp": "2026-08-01T11:00:00Z", "node_id": "node-01", "cpu_utilization_pct": 32.0, "memory_utilization_pct": 42.0},
        {"timestamp": "2026-08-01T12:00:00Z", "node_id": "node-01", "cpu_utilization_pct": 98.5, "memory_utilization_pct": 41.0}, # Anomaly spike
    ]

    processed, anomalies = detect_metric_anomalies(records)
    assert len(anomalies) >= 1
    assert anomalies[0]["anomaly_type"] == "CPU_SPIKE"
    assert anomalies[0]["severity"] == "CRITICAL"


# -------------------------------------------------------------------
# 2. User Feedback Submission Test
# -------------------------------------------------------------------
def test_api_submit_user_feedback(client):
    payload = {
        "item_id": "node-prod-01",
        "rating": 1,
        "comment": "Extremely helpful ARM Graviton recommendation!"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


# -------------------------------------------------------------------
# 3. Executive Report Export Test
# -------------------------------------------------------------------
def test_api_export_executive_report(client):
    response = client.get("/api/export-report")
    assert response.status_code == 200
    # Export is now a formatted HTML report (print-to-PDF ready) rather than raw JSON
    assert "text/html" in response.headers.get("content-type", "")
    html_content = response.text
    assert "Aegis AI" in html_content
    assert "Executive Infrastructure Capacity Report" in html_content
    assert "Forecast Accuracy Target" in html_content
    assert "FinOps Right-Sizing Advisory" in html_content
