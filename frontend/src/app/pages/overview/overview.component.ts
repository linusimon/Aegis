import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

declare var Chart: any;

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="tab-page active-page">
      <!-- Executive KPI Cards -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Cluster Health Score</div>
          <div class="metric-value">{{ healthScore }}</div>
          <div class="metric-badge badge-success">SLA Bounds Healthy</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Forecast Accuracy</div>
          <div class="metric-value">91.5%</div>
          <div class="metric-badge badge-success">Target ≥ 80% Met</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Monthly Cost Reduction</div>
          <div class="metric-value">-$619.00</div>
          <div class="metric-badge badge-success">24.5% Cost Reduction Met</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Infrastructure Nodes</div>
          <div class="metric-value">3 Nodes</div>
          <div class="metric-badge badge-warning">1 Over-Provisioned</div>
        </div>
      </div>

      <!-- Workload Preset Switcher Bar -->
      <div style="display: flex; gap: 16px; margin-bottom: 20px; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 13px; font-weight: 600; color: var(--text-secondary);">Workload Scenario Preset:</span>
          <button class="btn-tab" [class.active]="activePreset === 'saas_growth'" (click)="switchPreset('saas_growth')">SaaS Growth (+30%)</button>
          <button class="btn-tab" [class.active]="activePreset === 'memory_leak'" (click)="switchPreset('memory_leak')">Memory Leak Spike</button>
          <button class="btn-tab" [class.active]="activePreset === 'steady_state'" (click)="switchPreset('steady_state')">Normal Baseline</button>
        </div>
        <button class="btn-primary" (click)="triggerAnomalyCheck()" style="font-size: 12px; padding: 6px 12px;">Run Anomaly Detector</button>
      </div>

      <!-- Overview Chart & Anomaly Feed Grid -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <!-- Infrastructure Utilization Bar Chart -->
        <div class="panel-card" style="margin-bottom: 0;">
          <div class="panel-header">
            <h3 class="panel-title">Infrastructure Cluster Utilization Overview</h3>
          </div>
          <div class="chart-container">
            <canvas #overviewCanvas></canvas>
          </div>
        </div>

        <!-- Time-Series Anomaly Feed -->
        <div class="panel-card" style="margin-bottom: 0;">
          <div class="panel-header">
            <h3 class="panel-title">Time-Series Anomaly Feed</h3>
            <span class="metric-badge badge-success">{{ anomalies.length }} Outliers</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 10px; max-height: 280px; overflow-y: auto;">
            <div *ngFor="let item of anomalies" class="anomaly-item" [class.item-danger]="item.isHigh" [class.item-normal]="!item.isHigh">
              <div style="font-weight: 600; font-size: 12px;" [style.color]="item.isHigh ? 'var(--accent-rose)' : 'var(--accent-green)'">
                {{ item.node_id }} {{ item.isHigh ? 'Outlier Spike' : 'Baseline Normal' }}
              </div>
              <div style="font-size: 11px; color: var(--text-secondary);">
                CPU {{ item.cpu_utilization_pct?.toFixed(1) }}% | Memory {{ item.memory_utilization_pct?.toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 90-Day Historical Resource Utilization Trend Chart -->
      <div class="panel-card" style="margin-top: 20px;">
        <div class="panel-header">
          <h3 class="panel-title">90-Day Historical Resource Utilization Trend (Node-01)</h3>
          <span class="metric-badge badge-success">1,080 Records | MCP SQLite</span>
        </div>
        <div class="chart-container">
          <canvas #trendCanvas></canvas>
        </div>
      </div>

      <!-- Cluster Node Topology Panel -->
      <div class="panel-card" style="margin-top: 20px;">
        <div class="panel-header">
          <h3 class="panel-title">Cluster Infrastructure Node Topology & Instance Specs</h3>
          <span class="metric-badge badge-success">3 Active Nodes | AWS US-East-1</span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <!-- Node 1 -->
          <div class="anomaly-item item-normal" style="padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">Node-01</div>
              <span class="metric-badge badge-warning" style="font-size: 10px;">Over-Provisioned</span>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px;">Instance: <strong>c5.4xlarge (x86)</strong></div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Specs: 16 vCPU | 32 GB RAM | 500 GB NVMe</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">Zone: <code>us-east-1a</code> | Role: Primary App Server</div>
            <div style="margin-top: 10px; font-size: 11px; color: var(--accent-cyan); background: rgba(56, 189, 248, 0.1); padding: 6px 8px; border-radius: 4px;">
              Advisory: Right-size to <strong>c7g.2xlarge (ARM)</strong> -> Save $619/mo (-24.5%)
            </div>
          </div>

          <!-- Node 2 -->
          <div class="anomaly-item item-normal" style="padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">Node-02</div>
              <span class="metric-badge badge-success" style="font-size: 10px;">Balanced Load</span>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px;">Instance: <strong>c5.2xlarge (x86)</strong></div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Specs: 8 vCPU | 16 GB RAM | 250 GB NVMe</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">Zone: <code>us-east-1b</code> | Role: Task Worker Queue</div>
            <div style="margin-top: 10px; font-size: 11px; color: var(--accent-green); background: rgba(34, 197, 94, 0.1); padding: 6px 8px; border-radius: 4px;">
              Utilization 51.6% within safe SLA limits
            </div>
          </div>

          <!-- Node 3 -->
          <div class="anomaly-item item-normal" style="padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="font-weight: 700; font-size: 14px; color: var(--text-primary);">Node-03</div>
              <span class="metric-badge badge-success" style="font-size: 10px;">High Memory</span>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px;">Instance: <strong>m5.2xlarge (x86)</strong></div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Specs: 8 vCPU | 32 GB RAM | 250 GB NVMe</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">Zone: <code>us-east-1c</code> | Role: In-Memory Cache</div>
            <div style="margin-top: 10px; font-size: 11px; color: var(--accent-green); background: rgba(34, 197, 94, 0.1); padding: 6px 8px; border-radius: 4px;">
              Memory 62.1% stable allocation
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
          <div style="padding: 8px 16px; background: var(--bg-sidebar); border: 1px solid var(--border-color); border-radius: 20px; font-size: 11px; font-family: var(--font-mono); color: var(--text-muted); font-weight: 700;">
            __start__
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 10px 16px; background: var(--bg-sidebar); border: 2px solid var(--accent-cyan); border-radius: 8px; font-weight: 600; font-size: 13px;">
            Supervisor Router Hub
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 10px 16px; background: var(--bg-sidebar); border: 1px solid var(--border-color); border-radius: 8px; font-size: 12px;">
            Data Agent ➔ Forecast Agent ➔ Risk Agent ➔ FinOps Agent
          </div>
          <div style="color: var(--accent-green);">➔</div>
          <div style="padding: 8px 16px; background: var(--bg-sidebar); border: 1px solid var(--accent-green); border-radius: 20px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green); font-weight: 700;">
            __end__
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .chart-container {
      position: relative;
      height: 260px;
      width: 100%;
    }
  `]
})
export class OverviewComponent implements OnInit, AfterViewInit {
  @ViewChild('overviewCanvas') overviewCanvas!: ElementRef;
  @ViewChild('trendCanvas') trendCanvas!: ElementRef;

  activePreset = 'saas_growth';
  healthScore = '92/100';
  anomalies: any[] = [];
  overviewChart: any = null;
  trendChart: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadTelemetry();
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.initCharts();
    }, 100);
  }

  initCharts() {
    if (typeof Chart === 'undefined') return;

    if (this.overviewCanvas && this.overviewCanvas.nativeElement) {
      const ctx = this.overviewCanvas.nativeElement.getContext('2d');
      this.overviewChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Node-01 (c5.4xlarge)', 'Node-02 (c5.2xlarge)', 'Node-03 (m5.2xlarge)'],
          datasets: [
            { label: 'CPU Utilization %', data: [82.4, 51.6, 51.2], backgroundColor: '#06b6d4' },
            { label: 'Memory Utilization %', data: [74.5, 62.1, 58.4], backgroundColor: '#38bdf8' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } } },
            x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8', font: { family: 'Inter' } } }
          },
          plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
      });
    }

    if (this.trendCanvas && this.trendCanvas.nativeElement) {
      const ctx = this.trendCanvas.nativeElement.getContext('2d');
      const labels = Array.from({ length: 15 }, (_, i) => `Day ${i * 6 + 1}`);
      const cpuData = [45, 48, 52, 50, 56, 62, 60, 68, 72, 75, 78, 80, 82, 85, 84];
      const memData = [50, 52, 55, 54, 58, 60, 62, 65, 64, 68, 70, 72, 74, 75, 76];

      this.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            { label: 'CPU Utilization %', data: cpuData, borderColor: '#06b6d4', borderWidth: 2, tension: 0.3, fill: false },
            { label: 'Memory Utilization %', data: memData, borderColor: '#a78bfa', borderWidth: 2, tension: 0.3, fill: false }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } } },
            x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } } }
          },
          plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
      });
    }
  }

  loadTelemetry() {
    this.apiService.getMetrics(10).subscribe({
      next: (res) => {
        if (res.metrics) {
          this.anomalies = res.metrics.map((m: any) => ({
            ...m,
            isHigh: m.cpu_utilization_pct > 80 || m.memory_utilization_pct > 85
          }));
        }
      }
    });
  }

  switchPreset(preset: string) {
    this.activePreset = preset;
    let cpuData = [82.4, 51.6, 51.2];
    let memData = [74.5, 62.1, 58.4];

    if (preset === 'saas_growth') {
      this.healthScore = '84/100';
      cpuData = [88.5, 64.2, 61.0];
      memData = [78.2, 68.5, 62.4];
    } else if (preset === 'memory_leak') {
      this.healthScore = '76/100';
      cpuData = [68.0, 52.0, 49.5];
      memData = [94.8, 63.0, 59.0];
    } else {
      this.healthScore = '98/100';
      cpuData = [52.0, 48.5, 46.0];
      memData = [54.1, 51.0, 49.2];
    }

    if (this.overviewChart) {
      this.overviewChart.data.datasets[0].data = cpuData;
      this.overviewChart.data.datasets[1].data = memData;
      this.overviewChart.update();
    }

    this.apiService.generateSyntheticPreset(preset).subscribe();
  }

  triggerAnomalyCheck() {
    this.loadTelemetry();
  }
}
