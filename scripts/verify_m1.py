#!/usr/bin/env python3
"""Verification Script for Milestone 1: Environment & Architecture Setup."""
import sys
from datetime import datetime, timedelta, timezone

def run_verification():
    print("==================================================================")
    print("  Milestone 1 Verification: Data Schemas & Environment Setup  ")
    print("==================================================================")

    # 1. Test Schema Imports
    try:
        from app.schemas.metrics import MetricRecord, MetricBatch, SyntheticMetricConfig
        from app.schemas.forecast import ForecastPoint, ForecastResult
        from app.schemas.risk import TimeToExhaustion, NodeRiskAssessment, ClusterRiskSummary
        from app.schemas.finops import OptimizationAction, FinOpsReport
        from app.schemas.state import AgentState
        print("[SUCCESS] All Pydantic data schemas imported successfully.")
    except Exception as e:
        print(f"[FAIL] Schema import failed: {e}")
        sys.exit(1)

    # 2. Instantiate and validate sample metric record
    try:
        now = datetime.now(timezone.utc)
        record = MetricRecord(
            timestamp=now,
            node_id="node-prod-01",
            cpu_utilization_pct=78.5,
            memory_utilization_pct=88.2,
            storage_utilization_gb=450.0,
            storage_capacity_gb=500.0,
            network_in_mbps=120.4,
            network_out_mbps=85.1,
            anonymized=True
        )
        assert record.node_id == "node-prod-01"
        assert record.cpu_utilization_pct == 78.5
        print(f"[SUCCESS] MetricRecord validation passed: {record.node_id}")
    except Exception as e:
        print(f"[FAIL] MetricRecord validation error: {e}")
        sys.exit(1)

    # 3. Test ForecastResult Target Accuracy check
    try:
        forecast_result = ForecastResult(
            node_id="node-prod-01",
            horizon_days=30,
            model_type="Holt-Winters-ExponentialSmoothing",
            points=[
                ForecastPoint(
                    timestamp=now + timedelta(days=1),
                    predicted_cpu_pct=80.0,
                    lower_bound_cpu=75.0,
                    upper_bound_cpu=85.0,
                    predicted_memory_pct=89.0,
                    lower_bound_memory=85.0,
                    upper_bound_memory=93.0,
                    predicted_storage_gb=460.0
                )
            ],
            mape_score=8.5,
            rmse_score=2.1,
            accuracy_pct=91.5
        )
        assert forecast_result.target_accuracy_met is True, "Target accuracy >= 80% should be True"
        print(f"[SUCCESS] ForecastResult validation passed: Accuracy {forecast_result.accuracy_pct}% (Target Met: {forecast_result.target_accuracy_met})")
    except Exception as e:
        print(f"[FAIL] ForecastResult validation error: {e}")
        sys.exit(1)

    # 4. Test FinOpsReport Target Savings check
    try:
        action = OptimizationAction(
            node_id="node-prod-01",
            action_type="RIGHTSIZE_DOWN",
            current_instance_type="c5.4xlarge",
            recommended_instance_type="c6g.2xlarge",
            current_monthly_cost=610.0,
            projected_monthly_cost=420.0,
            monthly_savings_amount=190.0,
            savings_percentage=31.1,
            rationale="Average CPU utilization is 22% over last 30 days. Downsizing to ARM instance reduces cost by 31.1% while serving workload comfortably."
        )
        report = FinOpsReport(
            total_current_monthly_cost=2440.0,
            total_projected_monthly_cost=1680.0,
            total_monthly_savings=760.0,
            overall_savings_percentage=31.15,
            actions=[action]
        )
        assert report.target_savings_met is True, "Target savings >= 20% should be True"
        print(f"[SUCCESS] FinOpsReport validation passed: Savings {report.overall_savings_percentage}% (Target Met: {report.target_savings_met})")
    except Exception as e:
        print(f"[FAIL] FinOpsReport validation error: {e}")
        sys.exit(1)

    # 5. Check FastAPI App import
    try:
        from app.main import app
        assert app.title == "AI-Driven Infrastructure Capacity Planning Advisor API"
        print("[SUCCESS] FastAPI Application initialized successfully.")
    except Exception as e:
        print(f"[FAIL] FastAPI initialization failed: {e}")
        sys.exit(1)

    print("==================================================================")
    print("  ALL MILESTONE 1 VERIFICATION TESTS PASSED SUCCESSFULLY!          ")
    print("==================================================================")

if __name__ == "__main__":
    run_verification()
