"""Scenario Simulation Agent Node for LangGraph Multi-Agent Architecture.

Executes dynamic What-If stress tests (traffic surges, node scaling deltas, ARM migrations),
recalculates cost and risk impacts, and persists scenario logs into SQLite via MCP Client.
"""
import json
import asyncio
from typing import Dict, Any, Optional
from app.mcp_client import MCPDatabaseClient
from app.services.scenario_simulator import simulate_what_if_scenario


class ScenarioSimulationAgent:
    """Agent node responsible for What-If capacity stress tests and scenario modeling."""

    def __init__(self, mcp_client: Optional[MCPDatabaseClient] = None):
        self.mcp_client = mcp_client or MCPDatabaseClient()

    async def execute_simulation(
        self,
        traffic_multiplier: float = 1.5,
        capacity_delta_nodes: int = -1,
        arm_migration: bool = False
    ) -> Dict[str, Any]:
        """Execute What-If capacity stress test simulation.
        
        Args:
            traffic_multiplier: Traffic multiplier (e.g. 1.5 for +50% traffic).
            capacity_delta_nodes: Node count adjustment (e.g. -2 or +3 nodes).
            arm_migration: True if simulating ARM Graviton architecture.
            
        Returns:
            Dictionary containing scenario simulation result payload.
        """
        # Query metrics, forecasts, risks, and finops via MCP stdio tools
        metrics_res = await self.mcp_client.call_tool("query_metrics", {"limit": 500})
        records = metrics_res.get("records", [])
        
        unique_nodes = list({r.get("node_id") for r in records if r.get("node_id")})
        if not unique_nodes:
            unique_nodes = ["Node-01", "Node-02", "Node-03"]

        forecasts = []
        for node_id in unique_nodes:
            f_res = await self.mcp_client.call_tool("get_latest_forecast", {"node_id": node_id})
            forecasts.append(f_res.get("forecast", {"node_id": node_id, "points": []}))

        risk_res = await self.mcp_client.call_tool("get_latest_risk_assessment", {})
        risk_data = risk_res.get("risk_assessment", {"cluster_health_score": 90.0})

        finops_res = await self.mcp_client.call_tool("get_latest_finops_report", {})
        finops_data = finops_res.get("report", {"total_current_monthly_cost": 1000.0})

        # Run simulation engine
        sim_result = simulate_what_if_scenario(
            baseline_forecasts=forecasts,
            baseline_risk=risk_data,
            baseline_finops=finops_data,
            traffic_multiplier=traffic_multiplier,
            capacity_delta_nodes=capacity_delta_nodes,
            arm_migration=arm_migration
        )

        # Save simulation run log to SQLite via MCP stdio tool save_scenario_run
        await self.mcp_client.call_tool("save_scenario_run", {"scenario_json": json.dumps(sim_result)})

        return sim_result

    async def execute_agent_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution interface."""
        params = state.get("scenario_params", {})
        traffic = float(params.get("traffic_multiplier", 1.5))
        delta_nodes = int(params.get("capacity_delta_nodes", -1))
        arm = bool(params.get("arm_migration", False))

        sim_res = await self.execute_simulation(
            traffic_multiplier=traffic,
            capacity_delta_nodes=delta_nodes,
            arm_migration=arm
        )
        state["scenario_results"] = sim_res
        state["next_agent"] = "SupervisorAgent"
        return state
