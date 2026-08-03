# Cloud Compute Instance Specifications & Cost Reference Guide

## AWS Compute Instance Types

### Compute Optimized (c5 vs c6g Graviton)
- **c5.large**: 2 vCPU, 4.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$62.00 USD.
- **c5.xlarge**: 4 vCPU, 8.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$124.00 USD.
- **c5.2xlarge**: 8 vCPU, 16.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$248.00 USD.
- **c5.4xlarge**: 16 vCPU, 32.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$496.00 USD.
- **c6g.large (ARM Graviton2)**: 2 vCPU, 4.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$49.00 USD (21% Savings vs c5.large).
- **c6g.xlarge (ARM Graviton2)**: 4 vCPU, 8.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$98.00 USD (21% Savings vs c5.xlarge).
- **c6g.2xlarge (ARM Graviton2)**: 8 vCPU, 16.0 GB RAM, Network up to 10 Gbps. Monthly Cost: ~$196.00 USD (21% Savings vs c5.2xlarge).

### General Purpose (m5 vs m6g Graviton)
- **m5.large**: 2 vCPU, 8.0 GB RAM. Monthly Cost: ~$70.00 USD.
- **m5.xlarge**: 4 vCPU, 16.0 GB RAM. Monthly Cost: ~$140.00 USD.
- **m5.2xlarge**: 8 vCPU, 32.0 GB RAM. Monthly Cost: ~$280.00 USD.
- **m6g.xlarge (ARM Graviton2)**: 4 vCPU, 16.0 GB RAM. Monthly Cost: ~$111.00 USD (21% Savings vs m5.xlarge).
- **m6g.2xlarge (ARM Graviton2)**: 8 vCPU, 32.0 GB RAM. Monthly Cost: ~$222.00 USD (21% Savings vs m5.2xlarge).

### Memory Optimized (r5 vs r6g Graviton)
- **r5.xlarge**: 4 vCPU, 32.0 GB RAM. Monthly Cost: ~$184.00 USD.
- **r5.2xlarge**: 8 vCPU, 64.0 GB RAM. Monthly Cost: ~$368.00 USD.
- **r6g.xlarge (ARM Graviton2)**: 4 vCPU, 32.0 GB RAM. Monthly Cost: ~$147.00 USD (20% Savings vs r5.xlarge).

## Azure & GCP Equivalent Compute Reference
- **Azure D-Series / E-Series**: Similar vCPU to RAM ratios. Azure Arm-based Ampere Altra instances yield ~20% cost savings over x86.
- **GCP N2 / T2A (ARM)**: Tau T2A ARM instances provide ~20-25% cost-performance improvement over N2 x86 instances.
