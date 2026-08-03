"""Pytest Test Suite for Milestone 8: Supervisor Agent & LangGraph StateGraph Workflow Routing."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.workflow import capacity_advisor_graph, route_next_agent
from app.schemas.state import AgentState
from app.services.synthetic_generator import generate_synthetic_metrics, SyntheticMetricConfig


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------
# 1. Supervisor Agent Unit Tests
# -------------------------------------------------------------------
def test_supervisor_routing_logic():
    supervisor = SupervisorAgent()

    # Initial state -> DataProcessingAgent
    s1 = {"current_step": "start", "user_query": "Audit infrastructure metrics"}
    assert supervisor.determine_next_node(s1) == "DataProcessingAgent"

    # Simulation query -> ScenarioSimulationAgent
    s2 = {"current_step": "start", "user_query": "What if traffic increases by 50%?"}
    assert supervisor.determine_next_node(s2) == "ScenarioSimulationAgent"

    # Pipeline progression
    s3 = {"current_step": "DataProcessingAgent"}
    assert supervisor.determine_next_node(s3) == "ForecastingAgent"

    s4 = {"current_step": "ForecastingAgent"}
    assert supervisor.determine_next_node(s4) == "RiskAssessmentAgent"

    s5 = {"current_step": "RiskAssessmentAgent"}
    assert supervisor.determine_next_node(s5) == "FinOpsAgent"


@pytest.mark.asyncio
async def test_supervisor_executive_summary():
    supervisor = SupervisorAgent()
    mock_state = {
        "user_query": "Audit capacity and suggest right-sizing",
        "forecast_results": [{"accuracy_pct": 92.5}],
        "risk_assessment": {"cluster_health_score": 90.0, "critical_nodes_count": 0},
        "finops_report": {"total_monthly_savings": 450.0, "overall_savings_percentage": 28.5, "target_savings_met": True}
    }
    summary = await supervisor.generate_executive_summary(mock_state)
    assert "Executive Capacity Planning Report" in summary or "Report" in summary
    assert summary != ""


# -------------------------------------------------------------------
# 2. LangGraph StateGraph Workflow Execution Tests
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_compiled_langgraph_workflow():
    batch = generate_synthetic_metrics(SyntheticMetricConfig(num_nodes=2, duration_days=1, interval_minutes=120))
    initial_state = {
        "messages": [{"role": "user", "content": "Run full capacity evaluation"}],
        "user_query": "Run full capacity evaluation",
        "horizon_days": 7,
        "metrics_batch": batch.model_dump(mode="json"),
        "current_step": "start"
    }

    final_state = await capacity_advisor_graph.ainvoke(initial_state)

    assert "executive_summary" in final_state
    assert final_state.get("forecast_results") is not None
    assert final_state.get("risk_assessment") is not None
    assert final_state.get("finops_report") is not None


# -------------------------------------------------------------------
# 3. FastAPI Multi-Agent Chat Endpoint Tests
# -------------------------------------------------------------------
def test_api_agent_chat_endpoint(client):
    payload = {
        "query": "Run full multi-agent capacity planning audit and right-sizing report",
        "horizon_days": 7,
        "traffic_multiplier": 1.25
    }
    response = client.post("/api/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "executive_summary" in data
    assert data["forecast_accuracy_pct"] >= 80.0
    assert data["overall_savings_pct"] >= 20.0
    assert "details" in data
