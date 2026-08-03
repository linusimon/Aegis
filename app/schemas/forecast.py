from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ForecastPoint(BaseModel):
    """Single future prediction data point with confidence bounds."""
    timestamp: datetime = Field(..., description="Timestamp of the predicted metric")
    predicted_cpu_pct: float = Field(..., ge=0.0, le=100.0, description="Predicted CPU usage %")
    lower_bound_cpu: float = Field(..., ge=0.0, le=100.0, description="Lower 95% confidence limit for CPU %")
    upper_bound_cpu: float = Field(..., ge=0.0, le=100.0, description="Upper 95% confidence limit for CPU %")
    predicted_memory_pct: float = Field(..., ge=0.0, le=100.0, description="Predicted Memory usage %")
    lower_bound_memory: float = Field(..., ge=0.0, le=100.0, description="Lower 95% confidence limit for Memory %")
    upper_bound_memory: float = Field(..., ge=0.0, le=100.0, description="Upper 95% confidence limit for Memory %")
    predicted_storage_gb: float = Field(..., ge=0.0, description="Predicted Storage usage GB")


class ForecastResult(BaseModel):
    """Result payload of a time-series forecast execution."""
    node_id: str = Field(..., description="Node ID for which the forecast was computed")
    horizon_days: int = Field(..., ge=1, le=365, description="Forecast horizon in days (e.g. 7, 30, 90)")
    model_type: str = Field(..., description="Name of predictive model used (e.g., Holt-Winters, Prophet, Ridge)")
    points: List[ForecastPoint] = Field(..., description="List of predicted time-series points")
    mape_score: float = Field(..., ge=0.0, description="Mean Absolute Percentage Error (MAPE)")
    rmse_score: float = Field(..., ge=0.0, description="Root Mean Squared Error (RMSE)")
    accuracy_pct: float = Field(..., ge=0.0, le=100.0, description="Calculated model forecast accuracy % (Target >= 80%)")
    target_accuracy_met: bool = Field(default=False, description="True if accuracy_pct >= 80.0%")

    def model_post_init(self, __context) -> None:
        self.target_accuracy_met = (self.accuracy_pct >= 80.0)
