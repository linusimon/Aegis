"""FastAPI Routes for Interactive "What-If" Scenario Simulation."""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from app.agents.scenario_agent import ScenarioSimulationAgent

router = APIRouter(prefix="/api", tags=["Scenario Modeling API"])
scenario_agent = ScenarioSimulationAgent()


class ScenarioRequest(BaseModel):
    """Payload parameters for interactive What-If scenario stress test."""
    traffic_multiplier: float = Field(default=1.5, ge=0.1, le=5.0, description="Traffic multiplier (e.g. 1.5 for +50% traffic surge)")
    capacity_delta_nodes: int = Field(default=-1, ge=-10, le=20, description="Node count adjustment (e.g. -2 or +5 nodes)")
    arm_migration: bool = Field(default=False, description="True to simulate full ARM Graviton migration")


@router.post("/simulate")
async def run_scenario_simulation(req: ScenarioRequest):
    """Run interactive What-If capacity stress test simulation.
    
    Returns baseline vs simulated metrics, risk impact (SLA breach day & health index delta),
    and cost impact (monthly cost delta USD & %).
    """
    try:
        result = await scenario_agent.execute_simulation(
            traffic_multiplier=req.traffic_multiplier,
            capacity_delta_nodes=req.capacity_delta_nodes,
            arm_migration=req.arm_migration
        )
        return {
            "status": "success",
            "simulation": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario simulation execution failed: {str(e)}")
