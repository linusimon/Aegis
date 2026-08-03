"""Pytest Test Suite for Milestone 2: MCP SQLite Server over Stdio Transport."""
import json
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from app.mcp_client import MCPDatabaseClient


@pytest.fixture
def mcp_client():
    return MCPDatabaseClient()


# -------------------------------------------------------------------
# 1. Dynamic Discovery Tests (Tools, Resources, Prompts)
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_dynamic_tools_discovery(mcp_client):
    """Verify Client dynamically discovers all exposed MCP Tools at runtime."""
    tools = await mcp_client.list_tools()
    tool_names = [t["name"] for t in tools]
    
    assert "init_db" in tool_names
    assert "insert_metrics" in tool_names
    assert "query_metrics" in tool_names
    assert "save_forecast" in tool_names
    assert "get_latest_forecast" in tool_names
    assert "save_finops_report" in tool_names
    assert "get_latest_finops_report" in tool_names
    print(f"[SUCCESS] Dynamic Tool Discovery verified. Tools found: {len(tools)}")


@pytest.mark.asyncio
async def test_mcp_dynamic_resources_discovery(mcp_client):
    """Verify Client dynamically discovers all exposed MCP Resources at runtime."""
    resources = await mcp_client.list_resources()
    uris = [r["uri"] for r in resources]
    
    assert "schema://database" in uris
    assert "capacity://thresholds" in uris
    assert "capacity://cluster-summary" in uris
    print(f"[SUCCESS] Dynamic Resource Discovery verified. Resources found: {len(resources)}")


@pytest.mark.asyncio
async def test_mcp_dynamic_prompts_discovery(mcp_client):
    """Verify Client dynamically discovers all exposed MCP Prompts at runtime."""
    prompts = await mcp_client.list_prompts()
    prompt_names = [p["name"] for p in prompts]
    
    assert "capacity_audit_prompt" in prompt_names
    assert "finops_rightsizing_prompt" in prompt_names
    print(f"[SUCCESS] Dynamic Prompt Discovery verified. Prompts found: {len(prompts)}")


# -------------------------------------------------------------------
# 2. Passive Context Reading Tests (@mcp.resource)
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_read_database_schema_resource(mcp_client):
    """Verify passive context reading of database schema DDL via resource URI."""
    schema_text = await mcp_client.read_resource("schema://database")
    assert "TABLE metrics" in schema_text
    assert "TABLE forecasts" in schema_text
    assert "TABLE recommendations" in schema_text


@pytest.mark.asyncio
async def test_read_capacity_thresholds_resource(mcp_client):
    """Verify passive reading of capacity SLA breach thresholds."""
    thresholds_json = await mcp_client.read_resource("capacity://thresholds")
    data = json.loads(thresholds_json)
    assert data["sla_thresholds"]["cpu_critical_pct"] == 85.0
    assert data["sla_thresholds"]["memory_critical_pct"] == 90.0
    assert data["target_metrics"]["min_forecast_accuracy_pct"] == 80.0
    assert data["target_metrics"]["min_cost_savings_pct"] == 20.0


# -------------------------------------------------------------------
# 3. Executable Tool Operations over Stdio (@mcp.tool)
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_db_initialization_tool(mcp_client):
    """Verify init_db tool execution over stdio."""
    res = await mcp_client.call_tool("init_db", {})
    assert res["status"] == "success"


@pytest.mark.asyncio
async def test_mcp_insert_and_query_metrics_tool(mcp_client):
    """Verify metric insertion and querying via MCP stdio tools."""
    await mcp_client.call_tool("init_db", {})
    
    test_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node_id": "test-node-mcp-01",
        "cpu_utilization_pct": 82.4,
        "memory_utilization_pct": 89.1,
        "storage_utilization_gb": 350.0,
        "storage_capacity_gb": 500.0,
        "network_in_mbps": 45.0,
        "network_out_mbps": 30.0,
        "anonymized": True
    }
    
    # 1. Insert metric
    insert_res = await mcp_client.call_tool("insert_metrics", {"metrics_json": json.dumps([test_record])})
    assert insert_res["status"] == "success"
    assert insert_res["inserted_count"] == 1
    
    # 2. Query metric
    query_res = await mcp_client.call_tool("query_metrics", {"node_id": "test-node-mcp-01", "limit": 10})
    assert query_res["status"] == "success"
    assert query_res["total_records"] >= 1
    records = query_res["records"]
    assert records[0]["node_id"] == "test-node-mcp-01"
    assert records[0]["cpu_utilization_pct"] == 82.4


@pytest.mark.asyncio
async def test_mcp_save_and_get_forecast_tool(mcp_client):
    """Verify forecast persistence and lookup over stdio transport."""
    await mcp_client.call_tool("init_db", {})
    
    forecast_payload = {
        "node_id": "test-node-mcp-01",
        "horizon_days": 30,
        "model_type": "Holt-Winters-ExponentialSmoothing",
        "points": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "predicted_cpu_pct": 85.0,
                "lower_bound_cpu": 80.0,
                "upper_bound_cpu": 90.0,
                "predicted_memory_pct": 91.0,
                "lower_bound_memory": 87.0,
                "upper_bound_memory": 95.0,
                "predicted_storage_gb": 360.0
            }
        ],
        "mape_score": 4.5,
        "rmse_score": 1.2,
        "accuracy_pct": 95.5
    }
    
    save_res = await mcp_client.call_tool("save_forecast", {"forecast_json": json.dumps(forecast_payload)})
    assert save_res["status"] == "success"
    
    get_res = await mcp_client.call_tool("get_latest_forecast", {"node_id": "test-node-mcp-01"})
    assert get_res["status"] == "success"
    assert get_res["forecast"]["accuracy_pct"] >= 80.0
