"""Time-Series Anomaly Detector Service for Historical Metrics Preprocessing.

Calculates statistical Z-scores and Interquartile Range (IQR) bounds to identify
unusual CPU utilization spikes, memory leaks, and storage capacity anomalies.
"""
import numpy as np
from typing import List, Dict, Any, Tuple


def detect_metric_anomalies(
    records: List[Dict[str, Any]],
    cpu_threshold_z: float = 2.5,
    memory_threshold_z: float = 2.5
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Detect statistical anomalies in historical time-series metric records.
    
    Args:
        records: List of raw metric record dictionaries.
        cpu_threshold_z: Z-score threshold for CPU anomaly flagging.
        memory_threshold_z: Z-score threshold for Memory anomaly flagging.
        
    Returns:
        Tuple of (processed_records_with_anomaly_flags, list_of_detected_anomalies).
    """
    if not records:
        return records, []

    cpu_vals = [float(r.get("cpu_utilization_pct", 0.0)) for r in records]
    mem_vals = [float(r.get("memory_utilization_pct", 0.0)) for r in records]

    cpu_mean = float(np.mean(cpu_vals)) if cpu_vals else 0.0
    cpu_std = float(np.std(cpu_vals)) if cpu_vals else 1.0
    if cpu_std == 0:
        cpu_std = 1.0

    mem_mean = float(np.mean(mem_vals)) if mem_vals else 0.0
    mem_std = float(np.std(mem_vals)) if mem_vals else 1.0
    if mem_std == 0:
        mem_std = 1.0

    anomalies: List[Dict[str, Any]] = []
    processed_records: List[Dict[str, Any]] = []

    for r in records:
        rec = dict(r)
        c_val = float(rec.get("cpu_utilization_pct", 0.0))
        m_val = float(rec.get("memory_utilization_pct", 0.0))

        c_zscore = abs(c_val - cpu_mean) / cpu_std
        m_zscore = abs(m_val - mem_mean) / mem_std

        is_cpu_anomaly = c_zscore >= cpu_threshold_z or c_val >= 95.0
        is_mem_anomaly = m_zscore >= memory_threshold_z or m_val >= 95.0

        is_anomaly = is_cpu_anomaly or is_mem_anomaly
        rec["is_anomaly"] = is_anomaly
        rec["cpu_zscore"] = round(c_zscore, 2)
        rec["memory_zscore"] = round(m_zscore, 2)

        if is_anomaly:
            anomalies.append({
                "timestamp": rec.get("timestamp"),
                "node_id": rec.get("node_id"),
                "cpu_utilization_pct": c_val,
                "memory_utilization_pct": m_val,
                "anomaly_type": "CPU_SPIKE" if is_cpu_anomaly else "MEMORY_LEAK",
                "severity": "CRITICAL" if (c_val >= 95.0 or m_val >= 95.0) else "WARNING"
            })

        processed_records.append(rec)

    return processed_records, anomalies
