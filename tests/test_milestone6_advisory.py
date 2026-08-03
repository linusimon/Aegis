"""Pytest Test Suite for Milestone 6: Risk Assessment & FinOps Optimization Agents (Target >= 20% Savings)."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.finops_agent import FinOpsAgent


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Risk Assessment Agent Unit & Integration Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_risk_assessment_agent_tte_and_health_score():
    agent = RiskAssessmentAgent()
    
    # Mock forecast points breaching 85% CPU SLA on Day 5
    mock_points = [
        {"predicted_cpu_pct": 70.0 + (i * 4.0), "predicted_memory_pct": 50.0}
        for i in range(10)
    ]
    node_eval = await agent.evaluate_node_risk("node-prod-01", mock_points)
    
    assert node_eval.node_id == "node-prod-01"
    assert node_eval.risk_level in ["CRITICAL", "HIGH", "MEDIUM"]
    assert node_eval.health_score < 100.0
    
    cpu_ex = next(t for t in node_eval.exhaustion_metrics if t.resource_type == "CPU")
    assert cpu_ex.is_breached is True
    assert cpu_ex.days_remaining is not None
    assert cpu_ex.days_remaining <= 10


@pytest.mark.asyncio
async def test_risk_assessment_agent_cluster_workflow():
    agent = RiskAssessmentAgent()
    summary = await agent.evaluate_cluster_risk()
    assert summary.cluster_health_score >= 0.0
    assert summary.total_nodes >= 1


# -------------------------------------------------------------------
# 2. FinOps Agent Cost Reduction & RAG Citation Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_finops_agent_target_savings_and_rag_citations():
    agent = FinOpsAgent()
    report = await agent.generate_optimization_report()
    
    assert report.total_current_monthly_cost > 0.0
    assert report.total_monthly_savings > 0.0
    assert report.overall_savings_percentage >= 20.0  # Hackathon target >= 20%
    assert report.target_savings_met is True
    assert len(report.actions) > 0

    # Verify RAG Playbook citation is attached
    top_action = report.actions[0]
    assert top_action.rag_playbook_citation is not None
    assert top_action.savings_percentage > 0.0


# -------------------------------------------------------------------
# 3. FastAPI Advisory Endpoints Tests
# -------------------------------------------------------------------
def test_api_risk_assessment_endpoint(client):
    response = client.get("/api/risk-assessment")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "risk_assessment" in data


def test_api_finops_recommendations_endpoint(client):
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    report = data.get("report", {})
    assert report["overall_savings_percentage"] >= 20.0
    assert report["target_savings_met"] is True
