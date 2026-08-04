"""FastAPI Routes for Time-Series Forecasting Engine & Predictions."""
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.agents.forecast_agent import ForecastingAgent
from app.mcp_client import MCPDatabaseClient

router = APIRouter(prefix="/api", tags=["Time-Series Forecasting API"])
forecast_agent = ForecastingAgent()
mcp_client = MCPDatabaseClient()


from pydantic import BaseModel

class ForecastRequest(BaseModel):
    node_id: Optional[str] = None
    horizon_days: Optional[int] = 30


@router.post("/forecast")
@router.post("/v1/forecast")
async def trigger_forecast(
    req: Optional[ForecastRequest] = None,
    node_id: Optional[str] = Query(None, description="Optional specific node ID to forecast"),
    horizon_days: int = Query(30, ge=1, le=365, description="Forecast horizon in days (7, 30, 90)")
):
    """Trigger time-series forecasting engine.
    
    Generates predictions for CPU %, Memory %, and Storage GB with 95% confidence bounds,
    evaluates MAPE/RMSE accuracy, and persists results into SQLite via MCP Stdio Server.
    """
    try:
        target_node = req.node_id if req and req.node_id else node_id
        target_horizon = req.horizon_days if req and req.horizon_days else horizon_days

        if target_node:
            res = await forecast_agent.execute_forecast_for_node(target_node, horizon_days=target_horizon)
            return {
                "status": "success",
                "total_nodes_forecasted": 1,
                "forecasts": [res.model_dump(mode="json")]
            }
        else:
            results = await forecast_agent.execute_forecast_for_all_nodes(horizon_days=target_horizon)
            return {
                "status": "success",
                "total_nodes_forecasted": len(results),
                "forecasts": [r.model_dump(mode="json") for r in results]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting execution failed: {str(e)}")


@router.get("/forecast/{node_id}")
@router.get("/v1/forecast/{node_id}")
async def get_latest_node_forecast(
    node_id: str,
    horizon_days: int = Query(30, ge=1, le=365)
):
    """Retrieve forecast predictions for a server node from SQLite via MCP Server."""
    try:
        forecast_res = await forecast_agent.execute_forecast_for_node(node_id, horizon_days=horizon_days)
        return {"status": "success", "forecast": forecast_res.model_dump(mode="json")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast: {str(e)}")

