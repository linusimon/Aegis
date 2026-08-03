"""Pytest Test Suite for Data Preprocessing and Feature Engineering Service."""
import pytest
import pandas as pd
from app.services.preprocessing import telemetry_preprocessor, TelemetryPreprocessor
from app.services.forecasting import generate_node_forecast, calculate_mape_and_rmse


def test_remove_outliers_statistical_z_score():
    """Verify statistical Z-score outlier filtering in TelemetryPreprocessor."""
    data = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=10, freq="D"),
        "cpu_utilization_pct": [50.0, 52.0, 51.0, 49.0, 50.0, 53.0, 51.0, 50.0, 52.0, 999.0] # 999.0 is an extreme outlier
    })
    cleaned = telemetry_preprocessor.remove_outliers(data, "cpu_utilization_pct")
    assert len(cleaned) == 9
    assert 999.0 not in cleaned["cpu_utilization_pct"].values


def test_generate_lag_and_rolling_features():
    """Verify rolling mean and lag feature engineering."""
    data = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=10, freq="D"),
        "cpu_utilization_pct": [50.0 + i for i in range(10)]
    })
    res = telemetry_preprocessor.generate_lag_and_rolling_features(data, "cpu_utilization_pct")
    assert "rolling_mean_7d" in res.columns
    assert "rolling_std_7d" in res.columns
    assert "lag_1d" in res.columns
    assert "lag_7d" in res.columns


def test_prepare_rag_text_chunks():
    """Verify conversion of telemetry records into RAG text chunks."""
    records = [
        {"node_id": "Node-01", "timestamp": "2026-01-01", "cpu_utilization_pct": 61.7, "memory_utilization_pct": 74.5, "storage_used_gb": 250.0}
    ]
    chunks = telemetry_preprocessor.prepare_rag_text_chunks(records)
    assert len(chunks) == 1
    assert "Node-01" in chunks[0]
    assert "61.7%" in chunks[0]


def test_forecasting_service_alias():
    """Verify app.services.forecasting module alias works as expected."""
    mape, rmse, accuracy = calculate_mape_and_rmse([50.0, 60.0], [52.0, 58.0])
    assert mape > 0
    assert accuracy > 80.0
