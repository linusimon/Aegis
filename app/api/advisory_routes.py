"""FastAPI Routes for Infrastructure Risk Assessment and FinOps Cost Optimization Reports."""
import json
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.finops_agent import FinOpsAgent
from app.schemas.finops import FinOpsReport
from app.mcp_client import MCPDatabaseClient

router = APIRouter(prefix="/api", tags=["Risk & FinOps Advisory Reports"])
risk_agent = RiskAssessmentAgent()
finops_agent = FinOpsAgent()
mcp_client = MCPDatabaseClient()


@router.get("/risk-assessment")
@router.get("/v1/advisory/risk-assessment")
async def get_risk_assessment_report(
    cpu_limit: Optional[float] = None,
    mem_limit: Optional[float] = None
):
    """Retrieve infrastructure risk assessment report.
    
    Returns composite 0-100 Cluster Health Index, node risk levels (CRITICAL, HIGH, MEDIUM, LOW),
    Time-to-Exhaustion (TTE) in days, and SLA breach warnings from SQLite via MCP Server.
    """
    try:
        if cpu_limit is not None or mem_limit is not None:
            summary = await risk_agent.evaluate_cluster_risk(cpu_sla_limit=cpu_limit, mem_sla_limit=mem_limit)
            return {"status": "success", "risk_assessment": summary.model_dump(mode="json")}

        res = await mcp_client.call_tool("get_latest_risk_assessment", {})
        if res.get("status") == "not_found":
            summary = await risk_agent.evaluate_cluster_risk()
            return {"status": "success", "risk_assessment": summary.model_dump(mode="json")}

        return {"status": "success", "risk_assessment": res.get("risk_assessment")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk assessment: {str(e)}")


@router.get("/recommendations")
@router.get("/v1/advisory/recommendations")
@router.get("/right-sizing")
@router.get("/v1/advisory/right-sizing")
async def get_finops_optimization_report():

    """Retrieve FinOps cost optimization and right-sizing advisory report.
    
    Demonstrates >= 20% cost savings target with actionable recommendations grounded
    in RAG cloud vendor playbook citations.
    """
    try:
        res = await mcp_client.call_tool("get_latest_finops_report", {})
        if res.get("status") == "not_found":
            report = await finops_agent.generate_optimization_report()
            return {"status": "success", "report": report.model_dump(mode="json")}

        raw_report = res.get("report", {})
        report_obj = FinOpsReport.model_validate(raw_report)
        return {"status": "success", "report": report_obj.model_dump(mode="json")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch FinOps report: {str(e)}")
