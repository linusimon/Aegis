"""FastAPI Routes for Interactive What-If Capacity and FinOps Scenario Simulations."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query
from app.agents.scenario_agent import ScenarioSimulationAgent
from app.agents.forecast_agent import ForecastingAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.finops_agent import FinOpsAgent
from app.services.cost_model import compute_cost, compute_total_cost

router = APIRouter(prefix="/api", tags=["What-If Scenario Simulation API"])
scenario_agent = ScenarioSimulationAgent()
forecast_agent = ForecastingAgent()
risk_agent = RiskAssessmentAgent()
finops_agent = FinOpsAgent()


class WhatIfRequest(BaseModel):
    """Request payload for What-If scenario simulation."""
    workload_pct: float = Field(default=25.0, ge=-50.0, le=300.0, description="Projected workload growth percentage (e.g. 25.0 for +25% growth)")
    duration_days: int = Field(default=30, ge=1, le=365, description="Simulation duration in days")
    traffic_multiplier: Optional[float] = Field(default=None, description="Optional explicit traffic multiplier (overrides workload_pct if provided)")
    capacity_delta_nodes: int = Field(default=0, ge=-10, le=20, description="Node count change (e.g. -1 node, +2 nodes)")
    arm_migration: bool = Field(default=False, description="True to simulate full ARM Graviton migration")


@router.post("/whatif")
async def run_what_if_scenario(req: WhatIfRequest):
    """Run dynamic What-If capacity & cost simulation.
    
    Receives projected workload growth and capacity changes, calculates simulated resource demands,
    evaluates cost savings vs targets (≥ 20% savings), and returns scenario forecasts.
    """
    try:
        # Calculate effective traffic multiplier from workload_pct if not explicitly set
        traffic_mult = req.traffic_multiplier
        if traffic_mult is None:
            traffic_mult = round(1.0 + (req.workload_pct / 100.0), 2)

        # Run scenario simulation using ScenarioSimulationAgent engine
        sim_res = await scenario_agent.execute_simulation(
            traffic_multiplier=traffic_mult,
            capacity_delta_nodes=req.capacity_delta_nodes,
            arm_migration=req.arm_migration
        )

        simulated_cost = sim_res.get("simulated", {}).get("monthly_cost", 0.0)
        baseline_cost = sim_res.get("baseline", {}).get("monthly_cost", 0.0)

        # Cost savings calculation: savings % compared to baseline or unoptimized baseline
        if baseline_cost > 0:
            savings_pct = round(((baseline_cost - simulated_cost) / baseline_cost) * 100.0, 1)
        else:
            savings_pct = 0.0

        target_met = savings_pct >= 20.0 or sim_res.get("impact_deltas", {}).get("monthly_cost_delta", 0) < 0

        return {
            "status": "success",
            "scenario_name": f"Workload {req.workload_pct:+.1f}% ({req.duration_days}d Horizon)",
            "workload_pct": req.workload_pct,
            "duration_days": req.duration_days,
            "current_cost": baseline_cost,
            "projected_cost": simulated_cost,
            "monthly_cost_delta": sim_res.get("impact_deltas", {}).get("monthly_cost_delta", 0.0),
            "savings_pct": savings_pct,
            "target_met": target_met,
            "health_score": sim_res.get("simulated", {}).get("health_score", 90.0),
            "risk_severity": sim_res.get("simulated", {}).get("risk_severity", "LOW"),
            "earliest_sla_breach_day": sim_res.get("simulated", {}).get("earliest_sla_breach_day"),
            "forecasts": sim_res.get("simulated_forecasts", []),
            "simulation_details": sim_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"What-If scenario simulation failed: {str(e)}")
