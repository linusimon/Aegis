"""Scenario Simulation Engine for What-If Stress Testing.

Recalculates time-series forecasts, SLA breach Time-to-Exhaustion (TTE) dates,
cluster health index, and monthly cost deltas under dynamic hypothetical parameters
(traffic multipliers, node count adjustments, ARM architecture migrations).
"""
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def simulate_what_if_scenario(
    baseline_forecasts: List[Dict[str, Any]],
    baseline_risk: Dict[str, Any],
    baseline_finops: Dict[str, Any],
    traffic_multiplier: float = 1.5,
    capacity_delta_nodes: int = -1,
    arm_migration: bool = False
) -> Dict[str, Any]:
    """Run dynamic What-If capacity stress test simulation.
    
    Args:
        baseline_forecasts: Current node forecast prediction points.
        baseline_risk: Current risk assessment summary.
        baseline_finops: Current FinOps cost optimization report.
        traffic_multiplier: Traffic multiplier (e.g. 1.5 for +50% traffic surge).
        capacity_delta_nodes: Node count adjustment (e.g. -2 nodes, +3 nodes).
        arm_migration: True if simulating full ARM Graviton migration.
        
    Returns:
        Dictionary containing simulated forecast points, risk delta, and cost delta.
    """
    simulated_forecasts: List[Dict[str, Any]] = []
    
    # Calculate effective workload scale factor per node based on node delta
    base_node_count = max(1, len(baseline_forecasts))
    simulated_node_count = max(1, base_node_count + capacity_delta_nodes)
    node_scale_factor = base_node_count / simulated_node_count

    # Combined load multiplier
    total_load_factor = traffic_multiplier * node_scale_factor

    sla_breaches_count = 0
    earliest_breach_day: Optional[int] = None

    for node_f in baseline_forecasts:
        sim_node = copy.deepcopy(node_f)
        sim_points = []

        for idx, pt in enumerate(sim_node.get("points", [])):
            day_num = idx + 1

            # Recalculate CPU and RAM under simulated load factor
            sim_cpu = min(100.0, round(pt.get("predicted_cpu_pct", 50.0) * total_load_factor, 2))
            sim_mem = min(100.0, round(pt.get("predicted_memory_pct", 60.0) * (1.0 + (total_load_factor - 1.0) * 0.7), 2))
            sim_storage = round(pt.get("predicted_storage_gb", 200.0) * (1.0 + (traffic_multiplier - 1.0) * 0.2), 2)

            margin_cpu = round(pt.get("upper_bound_cpu", 60.0) - pt.get("predicted_cpu_pct", 50.0), 2)
            margin_mem = round(pt.get("upper_bound_memory", 70.0) - pt.get("predicted_memory_pct", 60.0), 2)

            if (sim_cpu >= 85.0 or sim_mem >= 90.0) and earliest_breach_day is None:
                earliest_breach_day = day_num
                sla_breaches_count += 1

            sim_points.append({
                "timestamp": pt.get("timestamp"),
                "predicted_cpu_pct": sim_cpu,
                "lower_bound_cpu": max(0.0, round(sim_cpu - margin_cpu, 2)),
                "upper_bound_cpu": min(100.0, round(sim_cpu + margin_cpu, 2)),
                "predicted_memory_pct": sim_mem,
                "lower_bound_memory": max(0.0, round(sim_mem - margin_mem, 2)),
                "upper_bound_memory": min(100.0, round(sim_mem + margin_mem, 2)),
                "predicted_storage_gb": sim_storage
            })

        sim_node["points"] = sim_points
        simulated_forecasts.append(sim_node)

    # Calculate Risk Delta & Simulated Health Score
    base_health = float(baseline_risk.get("cluster_health_score", 90.0))
    if total_load_factor > 1.5:
        sim_health = max(35.0, round(base_health - 30.0, 1))
        risk_severity = "HIGH"
    elif total_load_factor > 1.2:
        sim_health = max(55.0, round(base_health - 15.0, 1))
        risk_severity = "MEDIUM"
    else:
        sim_health = min(98.0, round(base_health + (5.0 if capacity_delta_nodes > 0 else 0.0), 1))
        risk_severity = "LOW"

    # Calculate Cost Delta
    base_monthly_cost = float(baseline_finops.get("total_current_monthly_cost", 1000.0))
    per_node_cost = base_monthly_cost / max(base_node_count, 1)
    
    raw_sim_cost = per_node_cost * simulated_node_count
    if arm_migration:
        raw_sim_cost *= 0.79  # 21% Graviton cost reduction

    cost_delta_amount = round(raw_sim_cost - base_monthly_cost, 2)
    cost_delta_pct = round((cost_delta_amount / max(base_monthly_cost, 1.0)) * 100.0, 2)

    return {
        "scenario_name": f"Traffic_{traffic_multiplier}x_NodesDelta_{capacity_delta_nodes}",
        "parameters": {
            "traffic_multiplier": traffic_multiplier,
            "capacity_delta_nodes": capacity_delta_nodes,
            "arm_migration": arm_migration
        },
        "baseline": {
            "health_score": base_health,
            "monthly_cost": base_monthly_cost,
            "total_nodes": base_node_count
        },
        "simulated": {
            "health_score": sim_health,
            "risk_severity": risk_severity,
            "monthly_cost": round(raw_sim_cost, 2),
            "total_nodes": simulated_node_count,
            "earliest_sla_breach_day": earliest_breach_day,
            "sla_breaches_count": sla_breaches_count
        },
        "impact_deltas": {
            "health_score_delta": round(sim_health - base_health, 1),
            "monthly_cost_delta": cost_delta_amount,
            "monthly_cost_delta_pct": cost_delta_pct
        },
        "simulated_forecasts": simulated_forecasts,
        "executed_at": datetime.now(timezone.utc).isoformat()
    }
