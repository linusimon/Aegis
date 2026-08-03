from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class OptimizationAction(BaseModel):
    """Specific right-sizing or scaling action to optimize cost and performance."""
    node_id: str = Field(..., description="Target node for optimization")
    action_type: str = Field(..., description="Type of action: RIGHTSIZE_DOWN, RIGHTSIZE_UP, AUTOSCALE, STORAGE_ARCHIVE, TERMINATE_IDLE")
    current_instance_type: str = Field(..., description="Current cloud instance tier / specs (e.g. c5.4xlarge)")
    recommended_instance_type: str = Field(..., description="Recommended instance tier / specs (e.g. c6g.2xlarge)")
    current_monthly_cost: float = Field(..., ge=0.0, description="Current monthly cost in USD")
    projected_monthly_cost: float = Field(..., ge=0.0, description="Projected monthly cost after action in USD")
    monthly_savings_amount: float = Field(..., ge=0.0, description="Projected monthly cost savings in USD")
    savings_percentage: float = Field(..., ge=0.0, le=100.0, description="Savings percentage for this node")
    rationale: str = Field(..., description="Analytical rationale explaining why this action is recommended")
    rag_playbook_citation: Optional[str] = Field(default=None, description="RAG-retrieved cloud vendor playbook / documentation reference")


class FinOpsReport(BaseModel):
    """Complete infrastructure cost optimization & savings report."""
    total_current_monthly_cost: float = Field(..., ge=0.0, description="Sum of current infrastructure monthly cost USD")
    total_projected_monthly_cost: float = Field(..., ge=0.0, description="Sum of projected infrastructure monthly cost USD")
    total_monthly_savings: float = Field(..., ge=0.0, description="Total projected monthly cost savings USD")
    overall_savings_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall cluster savings % (Target >= 20%)")
    target_savings_met: bool = Field(default=False, description="True if overall_savings_percentage >= 20.0%")
    actions: List[OptimizationAction] = Field(default_factory=list, description="List of actionable optimization recommendations")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report generation timestamp")

    def model_post_init(self, __context) -> None:
        self.target_savings_met = (self.overall_savings_percentage >= 20.0)
