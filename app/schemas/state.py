from typing import List, Dict, Any, Optional, TypedDict, Annotated
import operator
from app.schemas.metrics import MetricBatch
from app.schemas.forecast import ForecastResult
from app.schemas.risk import ClusterRiskSummary
from app.schemas.finops import FinOpsReport


class AgentState(TypedDict, total=False):
    """Global state container passed across Supervisor and Worker agents in LangGraph."""
    # Conversation / Workflow message history
    messages: Annotated[List[Dict[str, Any]], operator.add]
    
    # Active user request / intent
    user_query: str
    
    # Ingested dataset batch
    metrics_batch: Optional[Dict[str, Any]]
    data_agent_result: Optional[Dict[str, Any]]
    
    # Forecasting results per node
    forecast_results: Optional[List[Dict[str, Any]]]
    horizon_days: Optional[int]
    
    # Risk assessment report
    risk_assessment: Optional[Dict[str, Any]]
    
    # FinOps cost optimization report
    finops_report: Optional[Dict[str, Any]]
    
    # Scenario simulation parameters & output
    scenario_params: Optional[Dict[str, Any]]
    scenario_results: Optional[Dict[str, Any]]
    
    # Executive summary report
    executive_summary: Optional[str]
    
    # LangGraph routing supervision state
    next_agent: Optional[str]
    current_step: str
    errors: Optional[List[str]]
