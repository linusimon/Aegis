"""FastAPI Routes for Infrastructure Anomaly Diagnostics & Telemetry Spikes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.services.anomaly_detector import detect_metric_anomalies
from app.mcp_client import MCPDatabaseClient

router = APIRouter(prefix="/api", tags=["Anomaly Diagnostics API"])
mcp_client = MCPDatabaseClient()


@router.get("/anomalies")
async def get_detected_anomalies(
    node_id: Optional[str] = Query(None, description="Optional filter by node ID"),
    limit: int = Query(100, ge=1, le=1000, description="Max telemetry records to analyze")
):
    """Retrieve detected metric anomalies and spikes across historical telemetry.
    
    Uses statistical Z-Score and IQR outlier analysis to flag CPU spikes, memory leaks,
    and storage anomalies.
    """
    try:
        res = await mcp_client.call_tool("query_metrics", {"node_id": node_id or "", "limit": limit})
        records = res.get("records", [])

        processed, anomalies = detect_metric_anomalies(records)

        return {
            "status": "success",
            "total_records_analyzed": len(records),
            "anomalies_count": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect anomalies: {str(e)}")
