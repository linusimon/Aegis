# AWS Well-Architected Framework: FinOps Right-Sizing Playbook

## Section 1: Right-Sizing Evaluation Guidelines

### 1.1 CPU Over-Provisioning Criteria
- **Threshold**: Nodes with average CPU utilization below 25% over a 14-day evaluation window are flagged as over-provisioned.
- **Action**: Downsize by 1 instance size tier (e.g. from `c5.4xlarge` to `c5.2xlarge`) or migrate to ARM Graviton architecture (`c6g.2xlarge`).
- **Cost Impact**: Reduces monthly instance billing by 40% to 55% per node.

### 1.2 Memory Over-Provisioning Criteria
- **Threshold**: Nodes with maximum RAM utilization under 35% and zero swap usage.
- **Action**: Switch instance family from Memory-Optimized (`r5`) to General-Purpose (`m5` or `m6g`).
- **Cost Impact**: Reduces memory licensing/instance cost by 25% to 35%.

### 1.3 Graviton ARM Migration Policy
- **Policy**: For Linux workloads running Python, Node.js, Java, or Go, migrating from x86 (`c5`/`m5`/`r5`) to ARM Graviton (`c6g`/`m6g`/`r6g`) provides up to 20-40% better price-performance with zero code changes required.
- **Prerequisites**: Verify container images support `linux/arm64` architecture.

### 1.4 Auto-scaling & Idle Workload Termination
- **Idle Nodes**: Servers with CPU < 5% and Network throughput < 1 Mbps for 7 consecutive days should be terminated or snapshotted.
- **Auto-scaling Policy**: Enable Horizontal Pod Autoscaler (HPA) or EC2 Auto Scaling groups with scale-in thresholds at CPU < 30% and scale-out thresholds at CPU > 75%.
