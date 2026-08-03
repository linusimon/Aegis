"""Forecasting Agent Node for LangGraph Multi-Agent Architecture.

Queries time-series metrics via MCP Stdio Client, runs predictive forecasting models,
evaluates forecast accuracy (targeting >= 80%), and persists forecast predictions into SQLite.
"""
import json
import asyncio
from typing import Dict, Any, List, Optional
from app.mcp_client import MCPDatabaseClient
from app.services.forecasting_engine import generate_node_forecast
from app.schemas.forecast import ForecastResult


class ForecastingAgent:
    """Agent node responsible for time-series forecasting and accuracy evaluation."""

    def __init__(self, mcp_client: Optional[MCPDatabaseClient] = None):
        self.mcp_client = mcp_client or MCPDatabaseClient()

    async def execute_forecast_for_node(self, node_id: str, horizon_days: int = 30) -> ForecastResult:
        """Run forecast model for a target node and save prediction results via MCP stdio.
        
        Args:
            node_id: Target server node ID.
            horizon_days: Predictive horizon in days (7, 30, 90).
            
        Returns:
            ForecastResult payload object.
        """
        # 1. Query metric records from SQLite via MCP stdio tool
        query_res = await self.mcp_client.call_tool("query_metrics", {"node_id": node_id, "limit": 500})
        records = query_res.get("records", [])

        # 2. Run time-series forecasting model
        forecast_result = generate_node_forecast(records, node_id=node_id, horizon_days=horizon_days)

        # 3. Persist forecast prediction points & accuracy score into SQLite via MCP stdio tool
        forecast_dict = forecast_result.model_dump(mode="json")
        await self.mcp_client.call_tool("save_forecast", {"forecast_json": json.dumps(forecast_dict)})

        return forecast_result

    async def execute_forecast_for_all_nodes(self, horizon_days: int = 30) -> List[ForecastResult]:
        """Run forecasting workflow across all unique active server nodes."""
        summary_res = await self.mcp_client.call_tool("query_metrics", {"limit": 1000})
        records = summary_res.get("records", [])
        
        unique_nodes = list({r.get("node_id") for r in records if r.get("node_id")})
        if not unique_nodes:
            unique_nodes = ["Node-01"]

        results: List[ForecastResult] = []
        for node_id in unique_nodes:
            res = await self.execute_forecast_for_node(node_id, horizon_days=horizon_days)
            results.append(res)

        return results

    async def execute_agent_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution interface."""
        horizon_days = state.get("horizon_days", 30)
        results = await self.execute_forecast_for_all_nodes(horizon_days=horizon_days)
        
        state["forecast_results"] = [res.model_dump(mode="json") for res in results]
        state["next_agent"] = "RiskAssessmentAgent"
        return state
