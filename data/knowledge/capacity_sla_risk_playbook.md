# Capacity Planning & Infrastructure SLA Risk Mitigation Playbook

## Section 1: SLA Breach Thresholds & Risk Classifications

### 1.1 CPU Utilization Risk Boundaries
- **Warning Threshold (75% - 84%)**: Monitor node load, evaluate 7-day trend. Prepare auto-scaling group warm pool.
- **Critical Threshold (85% - 100%)**: High risk of latency degradation and broken SLAs.
- **Remediation**: Scale out node count (+1 to +2 instances) or up-size instance tier (`c5.xlarge` to `c5.2xlarge`) within 48 hours.

### 1.2 Memory Utilization Risk Boundaries
- **Warning Threshold (80% - 89%)**: Check for gradual application memory leaks.
- **Critical Threshold (90% - 100%)**: Critical risk of Out-Of-Memory (OOM) process termination by Linux kernel.
- **Remediation**: Immediate instance up-size to Memory-Optimized tier (`r5`/`r6g`) or container memory limit adjustment.

### 1.3 Storage Exhaustion Boundaries
- **Warning Threshold (85% - 94%)**: Disk space reaching capacity.
- **Critical Threshold (95% - 100%)**: Imminent database crash or filesystem write lock.
- **Remediation**: Expand EBS volume size or configure automated log rotation and S3 cold storage archive policies.

## Section 2: Time-To-Exhaustion (TTE) Action Playbook
- **TTE < 7 Days**: Immediate emergency intervention required. Alert DevOps on call.
- **TTE 7 - 14 Days**: High priority ticket. Schedule right-sizing or scaling action during next maintenance window.
- **TTE > 30 Days**: Normal operational monitoring. Include in monthly capacity report.
