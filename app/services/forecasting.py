"""Time-Series Forecasting Service Module for AI Capacity Planning Advisor.

Exposes time-series predictive forecasting algorithms (Holt-Winters & Ridge regression ensemble)
and accuracy evaluations (MAPE %, RMSE, Target ≥ 80% accuracy).
"""
from app.services.forecasting_engine import (
    generate_node_forecast,
    calculate_mape_and_rmse
)

__all__ = ["generate_node_forecast", "calculate_mape_and_rmse"]
