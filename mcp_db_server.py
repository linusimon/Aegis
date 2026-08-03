"""MCP SQLite Database Server over Stdio Transport for Infrastructure Capacity Advisor.

Implements all 3 MCP Primitives:
1. Tools (@mcp.tool): Executable functions for active DB queries and writes.
2. Resources (@mcp.resource): Passive context sources (DB schema, SLA thresholds, cluster summary).
3. Prompts (@mcp.prompt): Standardized prompt templates for agent workflows.
"""
import os
import json
import sqlite3
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("CapacityPlannerDB")

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "capacity_planner.db")


def get_db_connection() -> sqlite3.Connection:
    """Helper to create and return a SQLite database connection."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_sqlite_tables():
    """Create database tables and indices if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Metrics Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            node_id TEXT NOT NULL,
            cpu_utilization_pct REAL NOT NULL,
            memory_utilization_pct REAL NOT NULL,
            storage_utilization_gb REAL NOT NULL,
            storage_capacity_gb REAL NOT NULL,
            network_in_mbps REAL DEFAULT 0.0,
            network_out_mbps REAL DEFAULT 0.0,
            anonymized INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_node_time ON metrics(node_id, timestamp)")

    # 2. Forecasts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            horizon_days INTEGER NOT NULL,
            model_type TEXT NOT NULL,
            forecast_json TEXT NOT NULL,
            mape_score REAL NOT NULL,
            rmse_score REAL NOT NULL,
            accuracy_pct REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecasts_node ON forecasts(node_id)")

    # 3. Risks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_health_score REAL NOT NULL,
            total_nodes INTEGER NOT NULL,
            critical_nodes_count INTEGER NOT NULL,
            high_risk_nodes_count INTEGER NOT NULL,
            assessment_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 4. Recommendations / FinOps Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_current_monthly_cost REAL NOT NULL,
            total_projected_monthly_cost REAL NOT NULL,
            total_monthly_savings REAL NOT NULL,
            overall_savings_percentage REAL NOT NULL,
            actions_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 5. Scenarios Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_name TEXT NOT NULL,
            traffic_multiplier REAL NOT NULL,
            capacity_delta_nodes INTEGER NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 6. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Seed default Admin and User accounts if not present
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, created_at) VALUES ('admin', 'admin123', 'admin', ?)", (now_iso,))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, created_at) VALUES ('user', 'user123', 'user', ?)", (now_iso,))

    # Seed 30-day realistic historical telemetry records into SQLite metrics table if empty
    cursor.execute("SELECT COUNT(*) FROM metrics")
    metric_count = cursor.fetchone()[0]
    if metric_count == 0:
        import math
        base_time = datetime.now(timezone.utc) - timedelta(days=30)
        nodes_info = [
            ("Node-01", 42.0, 0.45, 6.0, 68.0, 250.0),
            ("Node-02", 50.0, 0.12, 3.5, 62.0, 150.0),
            ("Node-03", 45.0, 0.08, 5.0, 58.0, 180.0)
        ]
        for day_offset in range(30):
            t_dt = base_time + timedelta(days=day_offset)
            t_str = t_dt.isoformat()
            for node_id, cpu_start, slope, amp, mem_base, storage_gb in nodes_info:
                cpu_val = min(95.0, max(15.0, cpu_start + (day_offset * slope) + (amp * math.sin(2.0 * math.pi * day_offset / 7.0))))
                mem_val = min(95.0, max(20.0, mem_base + (day_offset * 0.1) + (3.0 * math.cos(2.0 * math.pi * day_offset / 7.0))))
                cursor.execute("""
                    INSERT INTO metrics (
                        timestamp, node_id, cpu_utilization_pct, memory_utilization_pct,
                        storage_utilization_gb, storage_capacity_gb, network_in_mbps, network_out_mbps,
                        anonymized, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (t_str, node_id, round(cpu_val, 2), round(mem_val, 2), round(storage_gb + day_offset * 0.8, 2), 500.0, 45.0, 60.0, now_iso))

    conn.commit()
    conn.close()


# Initialize database schema at startup
init_sqlite_tables()


# ===================================================================
# 1. MCP TOOLS (@mcp.tool) - Executable Database Operations
# ===================================================================

@mcp.tool()
async def init_db() -> str:
    """Initialize SQLite database tables and indices.
    
    Returns:
        JSON string confirming database status and path.
    """
    init_sqlite_tables()
    return json.dumps({
        "status": "success",
        "message": "Database tables and indexes initialized successfully.",
        "db_path": DB_PATH
    })


@mcp.tool()
async def insert_metrics(metrics_json: Any) -> str:
    """Bulk insert time-series resource utilization metric records into SQLite database.
    
    Args:
        metrics_json: JSON string of a list of metric records or a MetricBatch object.
        
    Returns:
        JSON string with insertion count status.
    """
    try:
        if isinstance(metrics_json, str):
            data = json.loads(metrics_json)
        else:
            data = metrics_json
        records = data.get("records", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            return json.dumps({"status": "error", "message": "Expected a list of metric records."})

        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        inserted = 0
        for r in records:
            cursor.execute("""
                INSERT INTO metrics (
                    timestamp, node_id, cpu_utilization_pct, memory_utilization_pct,
                    storage_utilization_gb, storage_capacity_gb, network_in_mbps, network_out_mbps,
                    anonymized, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("timestamp"),
                r.get("node_id"),
                float(r.get("cpu_utilization_pct", 0.0)),
                float(r.get("memory_utilization_pct", 0.0)),
                float(r.get("storage_utilization_gb", 0.0)),
                float(r.get("storage_capacity_gb", 100.0)),
                float(r.get("network_in_mbps", 0.0)),
                float(r.get("network_out_mbps", 0.0)),
                1 if r.get("anonymized", False) else 0,
                now_iso
            ))
            inserted += 1

        conn.commit()
        conn.close()
        return json.dumps({"status": "success", "inserted_count": inserted})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def query_metrics(node_id: str = "", limit: int = 100) -> str:
    """Query time-series metric records from the SQLite database.
    
    Args:
        node_id: Optional server node ID to filter metrics by.
        limit: Maximum number of recent records to return.
        
    Returns:
        JSON string containing the list of metric records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if node_id:
            cursor.execute("SELECT * FROM metrics WHERE node_id = ? ORDER BY timestamp DESC LIMIT ?", (node_id, limit))
        else:
            cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT ?", (limit,))

        rows = cursor.fetchall()
        conn.close()

        records = [dict(row) for row in rows]
        return json.dumps({"status": "success", "total_records": len(records), "records": records})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def save_forecast(forecast_json: Any) -> str:
    """Save time-series forecast results into the SQLite database.
    
    Args:
        forecast_json: JSON string of a ForecastResult object.
        
    Returns:
        JSON string confirming forecast record insertion.
    """
    try:
        if isinstance(forecast_json, str):
            data = json.loads(forecast_json)
        else:
            data = forecast_json
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO forecasts (
                node_id, horizon_days, model_type, forecast_json,
                mape_score, rmse_score, accuracy_pct, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("node_id"),
            int(data.get("horizon_days", 30)),
            data.get("model_type", "Time-Series-Model"),
            json.dumps(data.get("points", [])),
            float(data.get("mape_score", 0.0)),
            float(data.get("rmse_score", 0.0)),
            float(data.get("accuracy_pct", 0.0)),
            now_iso
        ))
        forecast_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return json.dumps({"status": "success", "forecast_id": forecast_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_latest_forecast(node_id: str) -> str:
    """Retrieve the most recent forecast predictions for a given node.
    
    Args:
        node_id: Target server node ID.
        
    Returns:
        JSON string containing the forecast payload.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM forecasts WHERE node_id = ? ORDER BY id DESC LIMIT 1", (node_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return json.dumps({"status": "not_found", "node_id": node_id})

        res = dict(row)
        res["points"] = json.loads(res["forecast_json"])
        del res["forecast_json"]
        return json.dumps({"status": "success", "forecast": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def save_risk_assessment(risk_json: Any) -> str:
    """Save cluster and node risk assessment results into the SQLite database.
    
    Args:
        risk_json: JSON string of ClusterRiskSummary object.
        
    Returns:
        JSON string confirming risk assessment persistence.
    """
    try:
        if isinstance(risk_json, str):
            data = json.loads(risk_json)
        else:
            data = risk_json
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO risks (
                cluster_health_score, total_nodes, critical_nodes_count,
                high_risk_nodes_count, assessment_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            float(data.get("cluster_health_score", 100.0)),
            int(data.get("total_nodes", 1)),
            int(data.get("critical_nodes_count", 0)),
            int(data.get("high_risk_nodes_count", 0)),
            json.dumps(data.get("node_assessments", [])),
            now_iso
        ))
        risk_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return json.dumps({"status": "success", "risk_id": risk_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_latest_risk_assessment() -> str:
    """Retrieve the most recent risk assessment report.
    
    Returns:
        JSON string containing the latest risk evaluation payload.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM risks ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return json.dumps({"status": "not_found"})

        res = dict(row)
        res["node_assessments"] = json.loads(res["assessment_json"])
        del res["assessment_json"]
        return json.dumps({"status": "success", "risk_assessment": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def save_user_feedback(feedback_json: Any) -> str:
    """Save user feedback rating (thumbs up/down) and comments into SQLite database.
    
    Args:
        feedback_json: JSON string containing rating (1 or -1), item_id, and feedback comment.
        
    Returns:
        JSON string confirming feedback persistence.
    """
    try:
        if isinstance(feedback_json, str):
            data = json.loads(feedback_json)
        else:
            data = feedback_json
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Ensure feedback table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                rating INTEGER,
                comment TEXT,
                created_at TEXT
            )
        """)

        cursor.execute("""
            INSERT INTO feedback (item_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            str(data.get("item_id", "general")),
            int(data.get("rating", 1)),
            str(data.get("comment", "")),
            now_iso
        ))
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return json.dumps({"status": "success", "feedback_id": feedback_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def save_scenario_run(scenario_json: Any) -> str:
    """Save scenario stress test simulation run log into SQLite database.
    
    Args:
        scenario_json: JSON string of scenario result payload.
        
    Returns:
        JSON string confirming scenario record persistence.
    """
    try:
        if isinstance(scenario_json, str):
            data = json.loads(scenario_json)
        else:
            data = scenario_json
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO scenarios (
                scenario_name, traffic_multiplier, capacity_delta_nodes,
                result_json, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("scenario_name", "what_if_simulation"),
            float(data.get("traffic_multiplier", 1.0)),
            int(data.get("capacity_delta_nodes", 0)),
            json.dumps(data),
            now_iso
        ))
        scenario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return json.dumps({"status": "success", "scenario_id": scenario_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def save_finops_report(report_json: Any) -> str:
    """Save FinOps cost optimization report into the SQLite database.
    
    Args:
        report_json: JSON string of a FinOpsReport object.
        
    Returns:
        JSON string confirming report persistence.
    """
    try:
        if isinstance(report_json, str):
            data = json.loads(report_json)
        else:
            data = report_json
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO recommendations (
                total_current_monthly_cost, total_projected_monthly_cost,
                total_monthly_savings, overall_savings_percentage,
                actions_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            float(data.get("total_current_monthly_cost", 0.0)),
            float(data.get("total_projected_monthly_cost", 0.0)),
            float(data.get("total_monthly_savings", 0.0)),
            float(data.get("overall_savings_percentage", 0.0)),
            json.dumps(data.get("actions", [])),
            now_iso
        ))
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return json.dumps({"status": "success", "report_id": report_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_latest_finops_report() -> str:
    """Retrieve the most recent FinOps cost optimization report.
    
    Returns:
        JSON string of the latest FinOps recommendations.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recommendations ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return json.dumps({"status": "not_found"})

        res = dict(row)
        res["actions"] = json.loads(res["actions_json"])
        del res["actions_json"]
        return json.dumps({"status": "success", "report": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def authenticate_user(username: str, password: str) -> str:
    """Authenticate user credentials and return role (admin or user).
    
    Args:
        username: Account username.
        password: Account password.
        
    Returns:
        JSON string containing authentication status, username, and role.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return json.dumps({"status": "failed", "message": "Invalid username or password."})

        return json.dumps({
            "status": "success",
            "username": row["username"],
            "role": row["role"]
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ===================================================================
# 2. MCP RESOURCES (@mcp.resource) - Passive State & Schema Context
# ===================================================================

@mcp.resource("schema://database")
async def get_database_schema() -> str:
    """Returns DDL schema definitions for all database tables."""
    return """
    -- SQLite Schema for Capacity Planning Advisor Database
    
    TABLE metrics (
        id INTEGER PRIMARY KEY, timestamp TEXT, node_id TEXT,
        cpu_utilization_pct REAL, memory_utilization_pct REAL,
        storage_utilization_gb REAL, storage_capacity_gb REAL,
        network_in_mbps REAL, network_out_mbps REAL, anonymized INTEGER
    );
    
    TABLE forecasts (
        id INTEGER PRIMARY KEY, node_id TEXT, horizon_days INTEGER,
        model_type TEXT, forecast_json TEXT, mape_score REAL,
        rmse_score REAL, accuracy_pct REAL, created_at TEXT
    );
    
    TABLE risks (
        id INTEGER PRIMARY KEY, cluster_health_score REAL, total_nodes INTEGER,
        critical_nodes_count INTEGER, high_risk_nodes_count INTEGER,
        assessment_json TEXT, created_at TEXT
    );
    
    TABLE recommendations (
        id INTEGER PRIMARY KEY, total_current_monthly_cost REAL,
        total_projected_monthly_cost REAL, total_monthly_savings REAL,
        overall_savings_percentage REAL, actions_json TEXT, created_at TEXT
    );
    """


@mcp.resource("capacity://thresholds")
async def get_capacity_thresholds() -> str:
    """Returns active SLA breach thresholds and risk boundary settings."""
    return json.dumps({
        "sla_thresholds": {
            "cpu_warning_pct": 75.0,
            "cpu_critical_pct": 85.0,
            "memory_warning_pct": 80.0,
            "memory_critical_pct": 90.0,
            "storage_warning_pct": 85.0,
            "storage_critical_pct": 95.0
        },
        "target_metrics": {
            "min_forecast_accuracy_pct": 80.0,
            "min_cost_savings_pct": 20.0
        }
    })


@mcp.resource("capacity://cluster-summary")
async def get_cluster_summary() -> str:
    """Returns live summary of stored cluster metrics and record counts."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT node_id) as nodes_count, COUNT(*) as total_records FROM metrics")
        row = cursor.fetchone()
        conn.close()

        return json.dumps({
            "unique_nodes": row["nodes_count"] if row else 0,
            "total_metric_records": row["total_records"] if row else 0,
            "db_status": "online"
        })
    except Exception as e:
        return json.dumps({"db_status": "error", "details": str(e)})


# ===================================================================
# 3. MCP PROMPTS (@mcp.prompt) - Standardized Agent Workflow Templates
# ===================================================================

@mcp.prompt("capacity_audit_prompt")
async def capacity_audit_prompt(node_id: str) -> str:
    """Generate prompt template for auditing node capacity and risk."""
    return f"""
    You are an AI Capacity Engineering Specialist.
    Perform a comprehensive capacity audit for server node: '{node_id}'.
    
    1. Query metrics for node '{node_id}' using the `query_metrics` tool.
    2. Check current CPU, Memory, and Storage usage against SLA thresholds (CPU > 85%, RAM > 90%).
    3. Calculate Time-to-Exhaustion (TTE) in days.
    4. Provide concrete risk mitigation recommendations.
    """


@mcp.prompt("finops_rightsizing_prompt")
async def finops_rightsizing_prompt() -> str:
    """Generate prompt template for FinOps right-sizing and cost reduction."""
    return """
    You are an expert FinOps Cloud Cost Architect.
    Generate right-sizing and cost optimization recommendations for the infrastructure.
    
    1. Retrieve forecasts and recent metric averages.
    2. Identify over-provisioned instance nodes.
    3. Target a MINIMUM of 20% overall cost reduction across the cluster.
    4. Include RAG playbook citations for cloud migration safety.
    """


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
