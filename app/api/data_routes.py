"""FastAPI Routes for Data Ingestion, Synthetic Generation, and Simulated Monitoring APIs."""
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from app.schemas.metrics import SyntheticMetricConfig, MetricBatch
from app.services.synthetic_generator import generate_synthetic_metrics
from app.services.data_parser import parse_metrics_file
from app.agents.data_agent import DataProcessingAgent
from app.mcp_client import MCPDatabaseClient

router = APIRouter(prefix="/api", tags=["Data Ingestion & Monitoring API"])
data_agent = DataProcessingAgent()
mcp_client = MCPDatabaseClient()


@router.post("/data/upload")
async def upload_metrics_file(
    file: UploadFile = File(...),
    anonymize: bool = Form(True)
):
    """Upload CSV or JSON historical monitoring logs file.
    
    Parses timestamps, normalizes metrics, anonymizes server hostnames/IPs,
    and stores records in SQLite via MCP Stdio Client.
    """
    try:
        content = await file.read()
        batch = parse_metrics_file(content, file.filename, anonymize=anonymize)
        result = await data_agent.process_and_store_batch(batch)
        return {
            "status": "success",
            "filename": file.filename,
            "anonymized": anonymize,
            "dataset_id": batch.dataset_id,
            "total_records": batch.total_records,
            "inserted_count": result.get("inserted_count", 0),
            "start_time": batch.start_time.isoformat() if batch.start_time else None,
            "end_time": batch.end_time.isoformat() if batch.end_time else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file upload: {str(e)}")


@router.post("/data/synthetic")
async def generate_synthetic_dataset(config: SyntheticMetricConfig):
    """Generate synthetic time-series metric datasets using workload profile presets.
    
    Presets:
    - saas_growth (linear trend up)
    - weekly_seasonality (24-hour daily seasonality curve)
    - black_friday_spike (sudden workload spikes)
    - memory_leak (gradual RAM leak on 1 server node)
    """
    try:
        batch = generate_synthetic_metrics(config)
        result = await data_agent.process_and_store_batch(batch)
        return {
            "status": "success",
            "config": config.model_dump(),
            "dataset_id": batch.dataset_id,
            "total_records": batch.total_records,
            "inserted_count": result.get("inserted_count", 0),
            "start_time": batch.start_time.isoformat() if batch.start_time else None,
            "end_time": batch.end_time.isoformat() if batch.end_time else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate synthetic metrics: {str(e)}")


# ===================================================================
# SIMULATED MONITORING TOOL REST APIs (Datadog & Prometheus format)
# ===================================================================

@router.get("/v1/monitoring/metrics")
async def get_simulated_monitoring_metrics(
    node_id: Optional[str] = Query(None, description="Optional node ID filter"),
    limit: int = Query(100, ge=1, le=1000, description="Max records limit")
):
    """Simulated Datadog / CloudWatch REST API endpoint.
    
    Reads historical resource utilization metrics from SQLite via MCP Server over stdio
    and returns standardized REST JSON payload.
    """
    try:
        res = await mcp_client.call_tool("query_metrics", {"node_id": node_id or "", "limit": limit})
        records = res.get("records", [])
        return {
            "status": "ok",
            "provider": "Simulated-Monitoring-API (Datadog/CloudWatch Compatible)",
            "query_node_id": node_id,
            "result_count": len(records),
            "metrics": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring API query error: {str(e)}")


@router.get("/v1/monitoring/prometheus/query")
async def get_simulated_prometheus_query(
    query: str = Query("cpu_utilization_pct", description="PromQL metric query (e.g. cpu_utilization_pct, memory_utilization_pct)")
):
    """Simulated Prometheus PromQL REST API endpoint.
    
    Returns standard Prometheus vector response format.
    """
    try:
        res = await mcp_client.call_tool("query_metrics", {"limit": 50})
        records = res.get("records", [])

        metric_name = "cpu_utilization_pct" if "cpu" in query.lower() else "memory_utilization_pct"
        result_vector = []

        for r in records:
            val = r.get(metric_name, 50.0)
            result_vector.append({
                "metric": {
                    "__name__": metric_name,
                    "instance": r.get("node_id", "node-01"),
                    "job": "infrastructure-capacity-monitor"
                },
                "value": [r.get("timestamp"), str(val)]
            })

        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": result_vector
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prometheus query error: {str(e)}")
