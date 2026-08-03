"""Comprehensive Unit & Integration Test Suite for Milestone 1."""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.metrics import MetricRecord, MetricBatch, SyntheticMetricConfig
from app.schemas.forecast import ForecastPoint, ForecastResult
from app.schemas.risk import TimeToExhaustion, NodeRiskAssessment, ClusterRiskSummary
from app.schemas.finops import OptimizationAction, FinOpsReport
from app.schemas.state import AgentState


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. FastAPI Health Endpoint Tests
# -------------------------------------------------------------------
def test_fastapi_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Infrastructure Capacity Planning Advisor"
    assert "timestamp" in data


# -------------------------------------------------------------------
# 2. Metric Schemas Tests (CPU, Memory, Storage, Anonymization)
# -------------------------------------------------------------------
def test_metric_record_valid():
    now = datetime.now(timezone.utc)
    record = MetricRecord(
        timestamp=now,
        node_id="srv-web-01",
        cpu_utilization_pct=45.2,
        memory_utilization_pct=62.8,
        storage_utilization_gb=120.0,
        storage_capacity_gb=500.0,
        network_in_mbps=50.0,
        network_out_mbps=40.0,
        anonymized=True,
    )
    assert record.node_id == "srv-web-01"
    assert record.cpu_utilization_pct == 45.2
    assert record.memory_utilization_pct == 62.8
    assert record.anonymized is True


def test_metric_record_invalid_cpu_pct():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        # CPU > 100% should trigger Pydantic validation error
        MetricRecord(
            timestamp=now,
            node_id="srv-invalid",
            cpu_utilization_pct=150.0,
            memory_utilization_pct=50.0,
            storage_utilization_gb=10.0,
            storage_capacity_gb=100.0,
        )


def test_metric_batch_time_range_auto_calculation():
    t1 = datetime.now(timezone.utc) - timedelta(hours=2)
    t2 = datetime.now(timezone.utc)
    r1 = MetricRecord(
        timestamp=t1, node_id="node-1", cpu_utilization_pct=30.0,
        memory_utilization_pct=40.0, storage_utilization_gb=10.0, storage_capacity_gb=100.0
    )
    r2 = MetricRecord(
        timestamp=t2, node_id="node-1", cpu_utilization_pct=50.0,
        memory_utilization_pct=60.0, storage_utilization_gb=15.0, storage_capacity_gb=100.0
    )
    batch = MetricBatch(dataset_id="ds-test-01", records=[r1, r2])
    assert batch.total_records == 2
    assert batch.start_time == t1
    assert batch.end_time == t2


# -------------------------------------------------------------------
# 3. Forecast Schema & 80% Accuracy Target Verification
# -------------------------------------------------------------------
def test_forecast_result_accuracy_target_met():
    now = datetime.now(timezone.utc)
    pt = ForecastPoint(
        timestamp=now + timedelta(days=7),
        predicted_cpu_pct=60.0, lower_bound_cpu=55.0, upper_bound_cpu=65.0,
        predicted_memory_pct=70.0, lower_bound_memory=65.0, upper_bound_memory=75.0,
        predicted_storage_gb=200.0
    )
    # High accuracy >= 80%
    result = ForecastResult(
        node_id="node-db-01", horizon_days=7, model_type="Prophet-Timeseries",
        points=[pt], mape_score=5.2, rmse_score=1.4, accuracy_pct=94.8
    )
    assert result.accuracy_pct >= 80.0
    assert result.target_accuracy_met is True


def test_forecast_result_accuracy_target_unmet():
    now = datetime.now(timezone.utc)
    pt = ForecastPoint(
        timestamp=now + timedelta(days=7),
        predicted_cpu_pct=60.0, lower_bound_cpu=40.0, upper_bound_cpu=80.0,
        predicted_memory_pct=70.0, lower_bound_memory=50.0, upper_bound_memory=90.0,
        predicted_storage_gb=200.0
    )
    # Low accuracy < 80%
    result = ForecastResult(
        node_id="node-db-01", horizon_days=7, model_type="LinearRegression",
        points=[pt], mape_score=25.0, rmse_score=12.0, accuracy_pct=75.0
    )
    assert result.accuracy_pct < 80.0
    assert result.target_accuracy_met is False


# -------------------------------------------------------------------
# 4. FinOps & 20% Cost Savings Target Verification
# -------------------------------------------------------------------
def test_finops_report_savings_target_met():
    action = OptimizationAction(
        node_id="node-app-01", action_type="RIGHTSIZE_DOWN",
        current_instance_type="m5.2xlarge", recommended_instance_type="m6g.xlarge",
        current_monthly_cost=280.0, projected_monthly_cost=154.0,
        monthly_savings_amount=126.0, savings_percentage=45.0,
        rationale="Node CPU averages 18% and RAM averages 35%. Downsizing to m6g.xlarge saves 45%.",
        rag_playbook_citation="AWS Well-Architected Cost Optimization Pillar Section 4.2"
    )
    report = FinOpsReport(
        total_current_monthly_cost=1000.0,
        total_projected_monthly_cost=750.0,
        total_monthly_savings=250.0,
        overall_savings_percentage=25.0,
        actions=[action]
    )
    assert report.overall_savings_percentage >= 20.0
    assert report.target_savings_met is True
    assert report.actions[0].rag_playbook_citation is not None
