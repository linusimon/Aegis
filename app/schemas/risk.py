from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TimeToExhaustion(BaseModel):
    """Calculated metric for resource threshold breach / capacity exhaustion."""
    resource_type: str = Field(..., description="Resource name: CPU, MEMORY, STORAGE")
    threshold_pct: float = Field(..., ge=0.0, le=100.0, description="Threshold percentage breaching SLA (e.g. 85%, 90%)")
    is_breached: bool = Field(default=False, description="True if currently or predicted to breach threshold")
    estimated_breach_timestamp: Optional[datetime] = Field(default=None, description="Predicted timestamp of breach")
    days_remaining: Optional[float] = Field(default=None, description="Days remaining until threshold breach")


class NodeRiskAssessment(BaseModel):
    """Risk evaluation for an individual server/node."""
    node_id: str = Field(..., description="Node identifier being evaluated")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Composite health index (100 = Optimal, 0 = Critical)")
    risk_level: str = Field(..., description="Risk severity level: LOW, MEDIUM, HIGH, CRITICAL")
    exhaustion_metrics: List[TimeToExhaustion] = Field(default_factory=list, description="Time-to-Exhaustion evaluations")
    risk_summary: str = Field(..., description="Human-readable risk summary")


class ClusterRiskSummary(BaseModel):
    """Aggregated risk assessment for the entire infrastructure cluster."""
    cluster_health_score: float = Field(..., ge=0.0, le=100.0, description="Average cluster health score")
    total_nodes: int = Field(..., ge=0, description="Total node count evaluated")
    critical_nodes_count: int = Field(default=0, ge=0, description="Count of nodes at CRITICAL risk level")
    high_risk_nodes_count: int = Field(default=0, ge=0, description="Count of nodes at HIGH risk level")
    node_assessments: List[NodeRiskAssessment] = Field(default_factory=list, description="Per-node risk evaluations")
