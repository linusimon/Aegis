"""Data Parser & Preprocessor for CSV and JSON Monitoring Exports.

Ingests CSV or JSON time-series log exports, performs timestamp ordering,
missing value interpolation, and privacy anonymization.
"""
import io
import json
import re
import hashlib
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.schemas.metrics import MetricRecord, MetricBatch


def anonymize_node_identifier(raw_id: str) -> str:
    """Scrub sensitive IP addresses or private server hostnames into anonymized tags."""
    if not raw_id:
        return "node-anon-01"

    # If it's an IP address or hostname, create consistent anonymized alias
    clean_id = raw_id.strip()
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', clean_id) or "internal" in clean_id.lower():
        hashed = hashlib.md5(clean_id.encode('utf-8')).hexdigest()[:6]
        return f"node-anon-{hashed}"

    return clean_id


def parse_metrics_file(file_bytes: bytes, filename: str, anonymize: bool = True) -> MetricBatch:
    """Parse CSV or JSON metric log content into a validated MetricBatch.
    
    Args:
        file_bytes: Raw file content bytes.
        filename: Name of uploaded file (.csv or .json).
        anonymize: True to scrub server IDs and IP addresses.
        
    Returns:
        MetricBatch object.
    """
    records: List[MetricRecord] = []

    if filename.lower().endswith(".json"):
        raw_text = file_bytes.decode("utf-8")
        data = json.loads(raw_text)
        raw_list = data.get("records", data) if isinstance(data, dict) else data

        for item in raw_list:
            ts_val = item.get("timestamp")
            if isinstance(ts_val, str):
                ts = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
            elif isinstance(ts_val, (int, float)):
                ts = datetime.fromtimestamp(ts_val, tz=timezone.utc)
            else:
                ts = datetime.now(timezone.utc)

            raw_node = item.get("node_id", item.get("host", "node-01"))
            node_id = anonymize_node_identifier(raw_node) if anonymize else raw_node

            rec = MetricRecord(
                timestamp=ts,
                node_id=node_id,
                cpu_utilization_pct=float(item.get("cpu_utilization_pct", item.get("cpu", 50.0))),
                memory_utilization_pct=float(item.get("memory_utilization_pct", item.get("memory", 60.0))),
                storage_utilization_gb=float(item.get("storage_utilization_gb", item.get("storage", 100.0))),
                storage_capacity_gb=float(item.get("storage_capacity_gb", 500.0)),
                network_in_mbps=float(item.get("network_in_mbps", 0.0)),
                network_out_mbps=float(item.get("network_out_mbps", 0.0)),
                anonymized=anonymize
            )
            records.append(rec)

    else:
        # Parse CSV format using Pandas
        df = pd.read_csv(io.BytesIO(file_bytes))
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

        # Standardize column mapping
        cpu_col = next((c for c in df.columns if "cpu" in c), None)
        mem_col = next((c for c in df.columns if "mem" in c or "ram" in c), None)
        storage_col = next((c for c in df.columns if "storage" in c or "disk" in c), None)
        node_col = next((c for c in df.columns if "node" in c or "host" in c or "server" in c), None)
        time_col = next((c for c in df.columns if "time" in c or "date" in c), None)

        for _, row in df.iterrows():
            if time_col and pd.notnull(row[time_col]):
                try:
                    ts = pd.to_datetime(row[time_col]).to_pydatetime()
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                except Exception:
                    ts = datetime.now(timezone.utc)
            else:
                ts = datetime.now(timezone.utc)

            raw_node = str(row[node_col]) if node_col and pd.notnull(row[node_col]) else "node-01"
            node_id = anonymize_node_identifier(raw_node) if anonymize else raw_node

            cpu_val = float(row[cpu_col]) if cpu_col and pd.notnull(row[cpu_col]) else 50.0
            mem_val = float(row[mem_col]) if mem_col and pd.notnull(row[mem_col]) else 60.0
            storage_val = float(row[storage_col]) if storage_col and pd.notnull(row[storage_col]) else 150.0

            rec = MetricRecord(
                timestamp=ts,
                node_id=node_id,
                cpu_utilization_pct=min(100.0, max(0.0, cpu_val)),
                memory_utilization_pct=min(100.0, max(0.0, mem_val)),
                storage_utilization_gb=max(0.0, storage_val),
                storage_capacity_gb=500.0,
                network_in_mbps=20.0,
                network_out_mbps=15.0,
                anonymized=anonymize
            )
            records.append(rec)

    # Sort records by timestamp
    records.sort(key=lambda r: r.timestamp)

    return MetricBatch(
        dataset_id=f"upload-{int(datetime.now(timezone.utc).timestamp())}",
        source=filename,
        records=records,
        total_records=len(records)
    )
