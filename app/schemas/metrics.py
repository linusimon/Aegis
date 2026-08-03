from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class MetricRecord(BaseModel):
    """Represents a single time-series resource utilization log record."""
    timestamp: datetime = Field(..., description="Timestamp of the metric observation")
    node_id: str = Field(..., description="Unique identifier for the server/node")
    cpu_utilization_pct: float = Field(..., ge=0.0, le=100.0, description="CPU usage percentage (0-100%)")
    memory_utilization_pct: float = Field(..., ge=0.0, le=100.0, description="RAM usage percentage (0-100%)")
    storage_utilization_gb: float = Field(..., ge=0.0, description="Storage used in GB")
    storage_capacity_gb: float = Field(..., gt=0.0, description="Total storage capacity in GB")
    network_in_mbps: float = Field(default=0.0, ge=0.0, description="Inbound network bandwidth in Mbps")
    network_out_mbps: float = Field(default=0.0, ge=0.0, description="Outbound network bandwidth in Mbps")
    anonymized: bool = Field(default=False, description="Flag indicating if node_id and identifiers are anonymized")

    @field_validator("storage_utilization_gb")
    @classmethod
    def validate_storage_limit(cls, v: float, info) -> float:
        if "storage_capacity_gb" in info.data and v > info.data["storage_capacity_gb"]:
            # Keep value but log/validate boundary
            pass
        return v


class MetricBatch(BaseModel):
    """Batch of historical metric records for analysis/ingestion."""
    dataset_id: str = Field(..., description="Unique identifier for this batch/dataset")
    source: str = Field(default="user_upload", description="Source of data (user_upload, synthetic, api_stream)")
    records: List[MetricRecord] = Field(..., description="List of time-series metric records")
    start_time: Optional[datetime] = Field(default=None, description="Earliest timestamp in batch")
    end_time: Optional[datetime] = Field(default=None, description="Latest timestamp in batch")
    total_records: int = Field(default=0, description="Total record count")

    def model_post_init(self, __context) -> None:
        if self.records and not self.total_records:
            self.total_records = len(self.records)
        if self.records and not self.start_time:
            timestamps = [r.timestamp for r in self.records]
            self.start_time = min(timestamps)
            self.end_time = max(timestamps)


class SyntheticMetricConfig(BaseModel):
    """Configuration for synthetic workload generation."""
    num_nodes: int = Field(default=5, ge=1, le=100, description="Number of server nodes to simulate")
    duration_days: int = Field(default=30, ge=1, le=365, description="Historical timespan in days")
    interval_minutes: int = Field(default=60, ge=1, le=1440, description="Frequency of metric data points")
    base_cpu_pct: float = Field(default=45.0, ge=5.0, le=90.0, description="Base average CPU utilization")
    base_memory_pct: float = Field(default=55.0, ge=5.0, le=90.0, description="Base average Memory utilization")
    base_storage_gb: float = Field(default=200.0, gt=0.0, description="Base storage used in GB")
    storage_capacity_gb: float = Field(default=1000.0, gt=0.0, description="Base total storage capacity")
    trend: str = Field(default="linear_up", description="Trend type: linear_up, linear_down, flat, exponential")
    seasonality: bool = Field(default=True, description="Enable 24-hour daily seasonality curve")
    spike_probability: float = Field(default=0.05, ge=0.0, le=0.5, description="Probability of transient workload spikes")
    memory_leak: bool = Field(default=False, description="Simulate gradual memory leak on one node")
