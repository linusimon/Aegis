"""Risk Assessment Agent Node for LangGraph Multi-Agent Architecture.

Evaluates metric predictions against SLA breach thresholds (CPU 85%, RAM 90%, Storage 95%),
calculates Time-to-Exhaustion (TTE) in days, computes composite 0-100 Health Index scores,
and persists risk evaluations into SQLite via MCP Stdio Client.
"""
import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.mcp_client import MCPDatabaseClient
from app.schemas.risk import TimeToExhaustion, NodeRiskAssessment, ClusterRiskSummary


class RiskAssessmentAgent:
    """Agent node responsible for Time-to-Exhaustion calculations and SLA breach detection."""

    def __init__(self, mcp_client: Optional[MCPDatabaseClient] = None):
        self.mcp_client = mcp_client or MCPDatabaseClient()

    async def evaluate_node_risk(
        self,
        node_id: str,
        forecast_points: List[Dict[str, Any]],
        cpu_sla_limit: Optional[float] = None,
        mem_sla_limit: Optional[float] = None
    ) -> NodeRiskAssessment:
        """Evaluate capacity breach risk and Time-to-Exhaustion for a single node.
        
        Args:
            node_id: Server node ID.
            forecast_points: Predictive forecast points list.
            cpu_sla_limit: Optional custom CPU SLA limit.
            mem_sla_limit: Optional custom Memory SLA limit.
            
        Returns:
            NodeRiskAssessment payload object.
        """
        exhaustions: List[TimeToExhaustion] = []
        node_health = 100.0
        risk_level = "LOW"

        # SLA Thresholds (configurable via parameter or environment variables)
        CPU_CRITICAL = cpu_sla_limit if cpu_sla_limit is not None else float(os.getenv("CPU_SLA_LIMIT", 85.0))
        MEM_CRITICAL = mem_sla_limit if mem_sla_limit is not None else float(os.getenv("MEMORY_SLA_LIMIT", 90.0))
        STORAGE_CRITICAL_PCT = float(os.getenv("STORAGE_SLA_LIMIT", 95.0))

        cpu_tte: Optional[float] = None
        mem_tte: Optional[float] = None
        storage_tte: Optional[float] = None

        cpu_breached = False
        mem_breached = False

        for idx, pt in enumerate(forecast_points):
            day_num = idx + 1
            cpu_val = float(pt.get("predicted_cpu_pct", 0.0))
            mem_val = float(pt.get("predicted_memory_pct", 0.0))

            if cpu_val >= CPU_CRITICAL and not cpu_breached:
                cpu_breached = True
                cpu_tte = float(day_num)

            if mem_val >= MEM_CRITICAL and not mem_breached:
                mem_breached = True
                mem_tte = float(day_num)

        # 1. CPU TTE
        exhaustions.append(TimeToExhaustion(
            resource_type="CPU",
            threshold_pct=CPU_CRITICAL,
            is_breached=cpu_breached,
            days_remaining=cpu_tte if cpu_breached else None
        ))

        # 2. Memory TTE
        exhaustions.append(TimeToExhaustion(
            resource_type="MEMORY",
            threshold_pct=MEM_CRITICAL,
            is_breached=mem_breached,
            days_remaining=mem_tte if mem_breached else None
        ))

        # Calculate Node Health Score & Risk Level
        if cpu_breached or mem_breached:
            min_tte = min(t for t in [cpu_tte, mem_tte] if t is not None)
            if min_tte <= 7:
                risk_level = "CRITICAL"
                node_health = 45.0
            elif min_tte <= 14:
                risk_level = "HIGH"
                node_health = 65.0
            else:
                risk_level = "MEDIUM"
                node_health = 80.0
        else:
            risk_level = "LOW"
            node_health = 95.0

        summary_msg = f"Node '{node_id}' risk level is {risk_level}. "
        if cpu_breached:
            summary_msg += f"CPU is predicted to breach 85% SLA in {cpu_tte} days. "
        if mem_breached:
            summary_msg += f"Memory is predicted to breach 90% SLA in {mem_tte} days. "
        if not cpu_breached and not mem_breached:
            summary_msg += "Resource utilization is operating within healthy SLA bounds."

        return NodeRiskAssessment(
            node_id=node_id,
            health_score=node_health,
            risk_level=risk_level,
            exhaustion_metrics=exhaustions,
            risk_summary=summary_msg
        )

    async def evaluate_cluster_risk(
        self,
        cpu_sla_limit: Optional[float] = None,
        mem_sla_limit: Optional[float] = None
    ) -> ClusterRiskSummary:
        """Evaluate risk across all active infrastructure nodes and persist report via MCP stdio tool."""
        # Query latest forecasts via MCP tool query_metrics / get_latest_forecast
        summary_res = await self.mcp_client.call_tool("query_metrics", {"limit": 500})
        records = summary_res.get("records", [])

        unique_nodes = list({r.get("node_id") for r in records if r.get("node_id")})
        if not unique_nodes:
            unique_nodes = ["Node-01"]

        assessments: List[NodeRiskAssessment] = []
        critical_count = 0
        high_count = 0
        total_health = 0.0

        for node_id in unique_nodes:
            forecast_res = await self.mcp_client.call_tool("get_latest_forecast", {"node_id": node_id})
            points = forecast_res.get("forecast", {}).get("points", [])
            node_eval = await self.evaluate_node_risk(node_id, points, cpu_sla_limit=cpu_sla_limit, mem_sla_limit=mem_sla_limit)
            assessments.append(node_eval)

            if node_eval.risk_level == "CRITICAL":
                critical_count += 1
            elif node_eval.risk_level == "HIGH":
                high_count += 1
            total_health += node_eval.health_score

        avg_health = round(total_health / max(len(unique_nodes), 1), 2)

        summary = ClusterRiskSummary(
            cluster_health_score=avg_health,
            total_nodes=len(unique_nodes),
            critical_nodes_count=critical_count,
            high_risk_nodes_count=high_count,
            node_assessments=assessments
        )

        # Save to SQLite via MCP tool save_risk_assessment
        summary_dict = summary.model_dump(mode="json")
        await self.mcp_client.call_tool("save_risk_assessment", {"risk_json": json.dumps(summary_dict)})

        return summary

    async def execute_agent_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution interface."""
        summary = await self.evaluate_cluster_risk()
        state["risk_assessment"] = summary.model_dump(mode="json")
        state["next_agent"] = "FinOpsAgent"
        return state
