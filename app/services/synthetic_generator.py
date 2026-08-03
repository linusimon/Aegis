"""Synthetic Time-Series Workload Metric Generator for Capacity Advisor.

Generates realistic time-series resource utilization metrics (CPU, Memory, Storage, Network)
supporting presets: SaaS Growth, Weekly Seasonality, Black Friday Spike, and Memory Leak.
"""
import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.schemas.metrics import MetricRecord, MetricBatch, SyntheticMetricConfig


def generate_synthetic_metrics(config: SyntheticMetricConfig) -> MetricBatch:
    """Generate a batch of synthetic time-series resource utilization records.
    
    Args:
        config: SyntheticMetricConfig specifying node count, duration, interval, and workload profile.
        
    Returns:
        MetricBatch containing generated time-series records.
    """
    records: List[MetricRecord] = []
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=config.duration_days)
    interval_td = timedelta(minutes=config.interval_minutes)

    total_steps = int((config.duration_days * 24 * 60) / config.interval_minutes)
    if total_steps < 1:
        total_steps = 1

    node_ids = [f"node-prod-{i+1:02d}" for i in range(config.num_nodes)]
    leak_node = node_ids[0] if config.memory_leak else None

    for step in range(total_steps):
        curr_time = start_time + (step * interval_td)
        progress = step / max(total_steps - 1, 1)

        # 1. Base trend factor
        if config.trend == "linear_up":
            trend_factor = 1.0 + (0.5 * progress)  # Grows by +50% over duration
        elif config.trend == "exponential":
            trend_factor = math.exp(0.5 * progress)
        elif config.trend == "linear_down":
            trend_factor = max(0.5, 1.0 - (0.4 * progress))
        else:
            trend_factor = 1.0

        # 2. Daily seasonality curve (24-hour cycle peak at 14:00 UTC)
        if config.seasonality:
            hour = curr_time.hour + (curr_time.minute / 60.0)
            season_factor = 0.8 + 0.4 * math.sin(math.pi * (hour - 8) / 12) if 8 <= hour <= 20 else 0.7
        else:
            season_factor = 1.0

        for node_id in node_ids:
            # 3. Random workload spike
            spike = 0.0
            if random.random() < config.spike_probability:
                spike = random.uniform(15.0, 35.0)

            # 4. CPU Calculation
            noise_cpu = random.uniform(-4.0, 4.0)
            cpu_pct = min(100.0, max(5.0, (config.base_cpu_pct * trend_factor * season_factor) + spike + noise_cpu))

            # 5. Memory Calculation
            noise_mem = random.uniform(-3.0, 3.0)
            mem_pct = config.base_memory_pct * season_factor + noise_mem

            # Simulate memory leak on target node if enabled
            if node_id == leak_node:
                leak_growth = progress * 35.0  # RAM grows by +35% over time
                mem_pct += leak_growth

            mem_pct = min(98.0, max(10.0, mem_pct))

            # 6. Storage Calculation (gradual accumulative growth)
            storage_growth = progress * (config.base_storage_gb * 0.25)
            noise_storage = random.uniform(-2.0, 2.0)
            storage_gb = min(
                config.storage_capacity_gb * 0.98,
                max(10.0, config.base_storage_gb + storage_growth + noise_storage)
            )

            # 7. Network Bandwidth Calculation
            net_in = max(1.0, (cpu_pct * 1.5) + random.uniform(-5.0, 10.0))
            net_out = max(1.0, (cpu_pct * 1.2) + random.uniform(-5.0, 8.0))

            record = MetricRecord(
                timestamp=curr_time,
                node_id=node_id,
                cpu_utilization_pct=round(cpu_pct, 2),
                memory_utilization_pct=round(mem_pct, 2),
                storage_utilization_gb=round(storage_gb, 2),
                storage_capacity_gb=config.storage_capacity_gb,
                network_in_mbps=round(net_in, 2),
                network_out_mbps=round(net_out, 2),
                anonymized=True
            )
            records.append(record)

    return MetricBatch(
        dataset_id=f"synthetic-{int(end_time.timestamp())}",
        source="synthetic_generator",
        records=records,
        start_time=start_time,
        end_time=end_time,
        total_records=len(records)
    )
