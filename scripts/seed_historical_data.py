"""Seed Script to populate SQLite database with 90 Days of High-Density Cluster Telemetry Data via MCP Client."""
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from app.mcp_client import MCPDatabaseClient
from app.schemas.metrics import MetricRecord, MetricBatch

mcp_client = MCPDatabaseClient()


async def seed_data():
    print("Initializing MCP Database...")
    await mcp_client.initialize_db_via_mcp()

    start_date = datetime.now(timezone.utc) - timedelta(days=90)
    records = []

    nodes = [
        {"id": "Node-01", "type": "c5.4xlarge", "base_cpu": 48.0, "growth": 0.35, "base_mem": 65.0},
        {"id": "Node-02", "type": "c5.2xlarge", "base_cpu": 35.0, "growth": 0.15, "base_mem": 52.0},
        {"id": "Node-03", "type": "m5.2xlarge", "base_cpu": 38.0, "growth": 0.12, "base_mem": 50.0, "leak_start": 60}
    ]

    for d in range(90):
        current_time = start_date + timedelta(days=d)
        for h in range(0, 24, 6): # 4 samples per day per node
            ts = current_time + timedelta(hours=h)
            time_str = ts.isoformat()

            # Seasonality sine wave
            seasonality = 8.0 * np.sin(2 * np.pi * h / 24)

            for node in nodes:
                # CPU Calculation
                cpu_val = node["base_cpu"] + (d * node["growth"]) + seasonality + np.random.normal(0, 2.5)
                cpu_val = max(10.0, min(98.0, cpu_val))

                # Memory Calculation
                mem_val = node["base_mem"] + (d * 0.1) + (seasonality * 0.4) + np.random.normal(0, 1.5)
                if "leak_start" in node and d >= node["leak_start"]:
                    mem_val += (d - node["leak_start"]) * 1.4 # Gradual memory leak

                mem_val = max(15.0, min(99.0, mem_val))

                # Storage calculation
                storage_val = 200.0 + (d * 1.8)

                records.append({
                    "timestamp": time_str,
                    "node_id": node["id"],
                    "instance_type": node["type"],
                    "cpu_utilization_pct": round(float(cpu_val), 2),
                    "memory_utilization_pct": round(float(mem_val), 2),
                    "storage_used_gb": round(float(storage_val), 2),
                    "network_io_mbps": round(float(120.0 + np.random.normal(0, 10)), 2),
                    "workload_type": "saas_growth" if d < 60 else "memory_leak_spike"
                })

    print(f"Inserting {len(records)} high-density telemetry records into SQLite via MCP Stdio Client...")
    res = await mcp_client.call_tool("insert_metrics", {"records": records})
    print(f"Successfully inserted {res.get('inserted_count', len(records))} records!")


if __name__ == "__main__":
    asyncio.run(seed_data())
