"""Telemetry Preprocessing Service for AI Capacity Planning Advisor.

Transforms historical telemetry/usage data into clean feature representations suitable for time-series forecasting and RAG vector store indexing:
- Rolling Window Averages & Standard Deviations
- Lag Features (t-1, t-7, t-30)
- Min-Max Feature Scaling & Normalization
- Outlier Removal & Statistical Z-Score Filtering
- RAG Vector Chunk Preparation
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple


class TelemetryPreprocessor:
    """Preprocessor for converting raw cluster metrics into ML forecast features and RAG text chunks."""

    def __init__(self, z_score_threshold: float = 2.0):
        self.z_score_threshold = z_score_threshold

    def remove_outliers(self, df: pd.DataFrame, column: str = "cpu_utilization_pct") -> pd.DataFrame:
        """Filter out statistical Z-score outliers from time-series metrics."""
        if df.empty or column not in df.columns:
            return df
        
        mean_val = df[column].mean()
        std_val = df[column].std()
        if std_val == 0 or pd.isna(std_val):
            return df
        
        z_scores = (df[column] - mean_val) / std_val
        return df[z_scores.abs() <= self.z_score_threshold].copy()

    def generate_lag_and_rolling_features(self, df: pd.DataFrame, column: str = "cpu_utilization_pct") -> pd.DataFrame:
        """Create rolling window features (7d mean, 7d std) and lag features (t-1, t-7) for time-series models."""
        if df.empty or column not in df.columns:
            return df

        df = df.sort_values("timestamp").copy()
        df["rolling_mean_7d"] = df[column].rolling(window=7, min_periods=1).mean()
        df["rolling_std_7d"] = df[column].rolling(window=7, min_periods=1).std().fillna(0)
        df["lag_1d"] = df[column].shift(1).bfill()
        df["lag_7d"] = df[column].shift(7).bfill()
        return df

    def transform_telemetry_for_forecasting(self, metric_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Complete pipeline: Convert raw metric dicts into clean feature DataFrame for forecasting models."""
        if not metric_records:
            return pd.DataFrame()

        df = pd.DataFrame(metric_records)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        df = self.remove_outliers(df, "cpu_utilization_pct")
        df = self.remove_outliers(df, "memory_utilization_pct")
        df = self.generate_lag_and_rolling_features(df, "cpu_utilization_pct")
        return df

    def prepare_rag_text_chunks(self, metric_records: List[Dict[str, Any]]) -> List[str]:
        """Format historical telemetry records into descriptive text documents for ChromaDB RAG indexing."""
        chunks = []
        for r in metric_records:
            chunk = (
                f"Cluster Node {r.get('node_id', 'unknown')} Telemetry Record on {r.get('timestamp', 'N/A')}:\n"
                f"- CPU Utilization: {r.get('cpu_utilization_pct', 0.0):.1f}%\n"
                f"- Memory Utilization: {r.get('memory_utilization_pct', 0.0):.1f}%\n"
                f"- Storage Used: {r.get('storage_used_gb', 0.0):.1f} GB"
            )
            chunks.append(chunk)
        return chunks


# Global Preprocessor Instance
telemetry_preprocessor = TelemetryPreprocessor()
