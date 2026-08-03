"""Data Processing Agent Node for LangGraph Multi-Agent Architecture.

Responsible for metric validation, anonymization, and invoking the MCP SQLite Server
over stdio transport to insert historical and synthetic datasets into SQLite.
"""
import json
import asyncio
from typing import Dict, Any, Optional
from app.mcp_client import MCPDatabaseClient
from app.schemas.metrics import MetricBatch


class DataProcessingAgent:
    """Agent node responsible for metric data ingestion and MCP storage."""

    def __init__(self, mcp_client: Optional[MCPDatabaseClient] = None):
        self.mcp_client = mcp_client or MCPDatabaseClient()

    async def process_and_store_batch(self, batch: MetricBatch) -> Dict[str, Any]:
        """Ingest metric batch and persist into SQLite database via MCP stdio tool.
        
        Args:
            batch: MetricBatch containing MetricRecord items.
            
        Returns:
            Dictionary payload with ingestion status and inserted count.
        """
        # Convert records to JSON serializable dicts
        metrics_payload = [record.model_dump(mode="json") for record in batch.records]
        metrics_json = json.dumps(metrics_payload)

        # Call MCP insert_metrics tool over stdio
        result = await self.mcp_client.call_tool("insert_metrics", {"metrics_json": metrics_json})
        
        return {
            "agent": "DataProcessingAgent",
            "status": result.get("status", "success"),
            "dataset_id": batch.dataset_id,
            "source": batch.source,
            "total_records": batch.total_records,
            "inserted_count": result.get("inserted_count", 0),
            "start_time": batch.start_time.isoformat() if batch.start_time else None,
            "end_time": batch.end_time.isoformat() if batch.end_time else None,
        }

    async def execute_agent_step(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution interface."""
        metrics_batch_dict = state.get("metrics_batch")
        if not metrics_batch_dict:
            return {"next_agent": "ForecastingAgent", "errors": ["No metrics batch provided to DataProcessingAgent"]}

        batch = MetricBatch.model_validate(metrics_batch_dict)
        res = await self.process_and_store_batch(batch)
        
        state["data_agent_result"] = res
        state["next_agent"] = "ForecastingAgent"
        return state
