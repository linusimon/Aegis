import os
from typing import Any

def _get_rate(var_name: str, default: float) -> float:
    """Fetch a rate from the environment, fallback to default if missing or invalid."""
    try:
        return float(os.getenv(var_name, default))
    except (TypeError, ValueError):
        return default

# Default rates (USD per unit per day). Can be overridden via .env.
CPU_RATE = _get_rate('CPU_RATE', 0.05)      # per CPU % point per day
MEMORY_RATE = _get_rate('MEMORY_RATE', 0.02)  # per Memory % point per day
STORAGE_RATE = _get_rate('STORAGE_RATE', 0.01)  # per GB per day

def compute_cost(cpu_pct: float, memory_pct: float, storage_gb: float) -> float:
    """Return the daily cost for a single forecast point.
    All rates are per‑day values; the function returns a daily cost in USD.
    """
    return cpu_pct * CPU_RATE + memory_pct * MEMORY_RATE + storage_gb * STORAGE_RATE

def compute_total_cost(forecast_points: Any) -> float:
    """Aggregate daily cost over an iterable of forecast point objects.
    Each point must expose ``predicted_cpu_pct``, ``predicted_memory_pct`` and ``predicted_storage_gb`` attributes.
    Returns total cost for the full horizon.
    """
    total = 0.0
    for pt in forecast_points:
        total += compute_cost(
            getattr(pt, 'predicted_cpu_pct', 0.0),
            getattr(pt, 'predicted_memory_pct', 0.0),
            getattr(pt, 'predicted_storage_gb', 0.0)
        )
    return total
