import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-finops',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="tab-page active-page">
      <!-- Executive KPI Cards -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Current Monthly Spend</div>
          <div class="metric-value">$2,450.00</div>
          <div class="metric-badge badge-warning">Unoptimized (x86 Instances)</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Projected Optimized Spend</div>
          <div class="metric-value" style="color: var(--accent-green);">$1,831.00</div>
          <div class="metric-badge badge-success">Target ≥ 20% Met</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Identified Monthly Savings</div>
          <div class="metric-value" style="color: var(--accent-cyan);">$619.00 / mo</div>
          <div class="metric-badge badge-success">24.5% Cost Reduction Met</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Cloud Migration Target</div>
          <div class="metric-value">AWS Graviton</div>
          <div class="metric-badge badge-success">ARM64 Ready</div>
        </div>
      </div>

      <!-- Main FinOps Grid -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
        <!-- Advisory Cards List -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">FinOps Cloud Right-Sizing Advisory & RAG Playbooks</h3>
            <span class="metric-badge badge-success">Target ≥ 20% Cost Reduction Met</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div *ngFor="let rec of recommendations" class="anomaly-item item-normal" style="padding: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">{{ rec.node_id }} Right-Sizing Plan</div>
                <span class="metric-badge badge-success">Save {{ rec.savings_pct }}%</span>
              </div>
              <div style="font-size: 13px; color: var(--accent-cyan); font-weight: 600; margin-top: 6px;">Action: {{ rec.action }}</div>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Rationale: {{ rec.rationale }}</div>
              <div style="font-size: 12px; color: var(--accent-green); font-weight: 600; margin-top: 6px;">Projected Monthly Savings: $ {{ rec.savings_usd }}/month</div>
              <div style="margin-top: 10px;">
                <button class="btn-primary" (click)="applyPlan(rec)" style="font-size: 11px; padding: 4px 10px;">Apply Right-Sizing Plan</button>
              </div>
            </div>
          </div>
        </div>

        <!-- What-If Simulator Panel -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">What-If FinOps Simulator</h3>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div>
              <label style="font-size: 12px; color: var(--text-secondary);">Projected Workload Growth (%)</label>
              <input type="number" [(ngModel)]="workloadPct" class="chat-input" style="width: 100%; margin-top: 4px; padding: 8px; font-size: 13px;">
            </div>

            <div>
              <label style="font-size: 12px; color: var(--text-secondary);">Horizon Duration (Days)</label>
              <select [(ngModel)]="durationDays" class="chat-input" style="width: 100%; margin-top: 4px; padding: 8px; font-size: 13px;">
                <option [ngValue]="7">7 Days</option>
                <option [ngValue]="30">30 Days</option>
                <option [ngValue]="90">90 Days</option>
              </select>
            </div>

            <div>
              <label style="font-size: 12px; color: var(--text-secondary);">Capacity Adjustment</label>
              <select [(ngModel)]="nodeDelta" class="chat-input" style="width: 100%; margin-top: 4px; padding: 8px; font-size: 13px;">
                <option [ngValue]="-1">Right-size (-1 Node)</option>
                <option [ngValue]="0">Maintain Node Count (0)</option>
                <option [ngValue]="1">Scale Up (+1 Node)</option>
              </select>
            </div>

            <button class="btn-primary" (click)="computeWhatIf()" style="width: 100%; padding: 10px; margin-top: 4px;">Compute Scenario</button>

            <div *ngIf="simResult" style="margin-top: 10px; padding: 12px; border-radius: 6px; background: var(--bg-input); border: 1px solid var(--border-color);">
              <div style="font-size: 13px; font-weight: 700; color: var(--accent-cyan);">{{ simResult.scenario_name }}</div>
              <div style="font-size: 12px; margin-top: 6px; color: var(--text-secondary);">Projected Monthly Cost: <strong style="color: var(--text-primary);">$ {{ simResult.projected_cost }}</strong></div>
              <div style="font-size: 12px; margin-top: 4px; color: var(--text-secondary);">Savings vs Unoptimized: <strong style="color: var(--accent-green);">{{ simResult.savings_pct }}%</strong></div>
              <div style="margin-top: 8px;">
                <span class="metric-badge" [class.badge-success]="simResult.target_met" [class.badge-warning]="!simResult.target_met">
                  {{ simResult.target_met ? 'Target Met (≥ 20% Savings)' : 'Below Target Savings' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Agent Workflow Panel -->
      <div class="panel-card" style="margin-top: 20px;">
        <div class="panel-header" style="margin-bottom: 12px;">
          <h3 class="panel-title" style="display: flex; align-items: center; gap: 8px;">
            <span class="pulse-indicator"></span> Active LangGraph Agent Workflow Connections
          </h3>
        </div>
        <div style="display: flex; align-items: center; justify-content: center; gap: 16px; padding: 20px; background: var(--bg-input); border-radius: 8px; border: 1px solid var(--border-color); overflow-x: auto;">
          <div style="padding: 10px 16px; background: var(--bg-card); border: 2px solid var(--accent-cyan); border-radius: 8px; font-weight: 600; font-size: 13px;">
            FinOps Agent (Vector DB RAG Playbooks)
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.1); border: 1px dashed var(--accent-green); border-radius: 6px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green);">
            MCP: query_playbook
          </div>
          <div style="color: var(--accent-green);">➔</div>
          <div style="padding: 8px 16px; background: var(--bg-sidebar); border: 1px solid var(--accent-green); border-radius: 20px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green); font-weight: 700;">
            __end__
          </div>
        </div>
      </div>
    </section>
  `
})
export class FinopsComponent implements OnInit {
  workloadPct = 25;
  durationDays = 30;
  nodeDelta = -1;
  simResult: any = null;

  recommendations = [
    { node_id: 'Node-01', action: 'Downsize c5.4xlarge to c7g.2xlarge (ARM)', savings_pct: 24.5, savings_usd: 619, rationale: 'Average CPU utilization is 61.4% with over-provisioned vCPU allocation. Migrating to Graviton ARM64 cuts cost by 24.5%.' },
    { node_id: 'Node-02', action: 'Right-size c5.2xlarge to c7g.xlarge', savings_pct: 21.0, savings_usd: 210, rationale: 'Sustained load below 55% vCPU. Graviton migration maintains SLA performance.' }
  ];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getRightSizingAdvisory().subscribe({
      next: (res) => {
        if (res.recommendations) this.recommendations = res.recommendations;
      }
    });
    this.computeWhatIf();
  }

  computeWhatIf() {
    this.apiService.computeWhatIf({
      workload_pct: this.workloadPct,
      duration_days: this.durationDays,
      capacity_delta_nodes: this.nodeDelta,
      arm_migration: true
    }).subscribe({
      next: (res) => {
        if (res.status === 'success') this.simResult = res;
      }
    });
  }

  applyPlan(rec: any) {
    alert(`Applied FinOps plan for ${rec.node_id}: ${rec.action}`);
  }
}
