import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-risk',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="tab-page active-page">
      <!-- Executive KPI Row -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Composite Cluster Health</div>
          <div class="metric-value">92/100</div>
          <div class="metric-badge badge-success">SLA Bounds Healthy</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">SLA Breach Risk</div>
          <div class="metric-value" style="color: var(--accent-green);">LOW</div>
          <div class="metric-badge badge-success">0 Impending Breaches</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">CPU SLA Threshold</div>
          <div class="metric-value" style="color: var(--accent-cyan);">{{ cpuLimit }}%</div>
          <div class="metric-badge badge-success">Max Safe Utilization</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Memory SLA Threshold</div>
          <div class="metric-value" style="color: var(--accent-cyan);">{{ memLimit }}%</div>
          <div class="metric-badge badge-success">Max Safe Allocation</div>
        </div>
      </div>

      <!-- Main Risk Grid -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
        <!-- SLA Threshold Sliders & Node Risk Cards -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">SLA Breach Warning & Infrastructure Risk Assessment</h3>
            <span class="metric-badge badge-success">MCP SQLite Database Sync</span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; padding: 16px; background: var(--bg-input); border-radius: 8px; border: 1px solid var(--border-color);">
            <div>
              <div class="control-label-row">
                <span>CPU Max SLA Limit (%)</span>
                <strong>{{ cpuLimit }}%</strong>
              </div>
              <input type="range" class="slider-input" min="50" max="95" step="1" [(ngModel)]="cpuLimit" (input)="updateRiskAssessment()">
            </div>

            <div>
              <div class="control-label-row">
                <span>Memory Max SLA Limit (%)</span>
                <strong>{{ memLimit }}%</strong>
              </div>
              <input type="range" class="slider-input" min="50" max="95" step="1" [(ngModel)]="memLimit" (input)="updateRiskAssessment()">
            </div>
          </div>

          <!-- Node Risk Cards -->
          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div *ngFor="let node of nodeRisks" class="anomaly-item" [class.item-danger]="node.risk === 'CRITICAL' || node.risk === 'HIGH'" [class.item-normal]="node.risk === 'LOW' || node.risk === 'MEDIUM'" style="padding: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">{{ node.node_id }} Risk Profile</div>
                <span class="metric-badge" [class.badge-danger]="node.risk === 'CRITICAL' || node.risk === 'HIGH'" [class.badge-success]="node.risk === 'LOW' || node.risk === 'MEDIUM'">
                  {{ node.risk }} Risk
                </span>
              </div>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px;">Instance Type: <strong>{{ node.instance_type }}</strong></div>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">Time-to-Exhaustion (TTE): <strong style="color: var(--accent-green);">{{ node.tte_days }} Days</strong></div>
              <div style="font-size: 11px; color: var(--accent-cyan); margin-top: 6px;">Recommendation: {{ node.recommendation }}</div>
            </div>
          </div>
        </div>

        <!-- Telemetry Log Stream Side-Panel -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Real-Time Telemetry Stream</h3>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; font-family: var(--font-mono); font-size: 11px; max-height: 380px; overflow-y: auto;">
            <div style="padding: 8px; background: var(--bg-input); border-radius: 4px; border-left: 3px solid var(--accent-green);">
              [INFO] Node-01 telemetry sync complete. CPU 82.4% | MEM 74.5%
            </div>
            <div style="padding: 8px; background: var(--bg-input); border-radius: 4px; border-left: 3px solid var(--accent-green);">
              [INFO] Node-02 telemetry sync complete. CPU 51.6% | MEM 62.1%
            </div>
            <div style="padding: 8px; background: var(--bg-input); border-radius: 4px; border-left: 3px solid var(--accent-green);">
              [INFO] Node-03 telemetry sync complete. CPU 51.2% | MEM 58.4%
            </div>
            <div style="padding: 8px; background: var(--bg-input); border-radius: 4px; border-left: 3px solid var(--accent-cyan);">
              [MCP] Executed tool get_latest_risk_assessment over SSE transport.
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
            Risk Assessment Agent (SLA & TTE Evaluator)
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.1); border: 1px dashed var(--accent-green); border-radius: 6px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green);">
            MCP: risk_assessment
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
export class RiskComponent implements OnInit {
  cpuLimit = 85;
  memLimit = 90;

  nodeRisks = [
    { node_id: 'Node-01', instance_type: 'c5.4xlarge (x86)', risk: 'LOW', tte_days: '>30', recommendation: 'Right-size to c7g.2xlarge ARM to reduce cost by 24.5%.' },
    { node_id: 'Node-02', instance_type: 'c5.2xlarge (x86)', risk: 'LOW', tte_days: '>30', recommendation: 'Maintain current specs or right-size to c7g.xlarge ARM.' },
    { node_id: 'Node-03', instance_type: 'm5.2xlarge (x86)', risk: 'LOW', tte_days: '>30', recommendation: 'High memory allocation stable at 62.1%.' }
  ];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.updateRiskAssessment();
  }

  updateRiskAssessment() {
    this.apiService.getRiskAssessment(this.cpuLimit, this.memLimit).subscribe({
      next: (res) => {
        if (res.risk_assessment && res.risk_assessment.nodes) {
          this.nodeRisks = res.risk_assessment.nodes;
        }
      }
    });
  }
}
