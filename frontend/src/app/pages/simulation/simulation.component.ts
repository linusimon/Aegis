import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

declare var Chart: any;

@Component({
  selector: 'app-simulation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="tab-page active-page">
      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 24px;">
        <!-- Controls Side-Panel -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Simulation Controls</h3>
          </div>

          <div class="control-group">
            <div class="control-label-row">
              <span>Traffic Surge Multiplier</span>
              <strong>{{ trafficSurge }}x</strong>
            </div>
            <input type="range" class="slider-input" min="0.5" max="3.0" step="0.1" [(ngModel)]="trafficSurge" (input)="updateScenario()">
          </div>

          <div class="control-group">
            <div class="control-label-row">
              <span>Capacity Node Delta</span>
              <strong>{{ nodeDelta }} Node(s)</strong>
            </div>
            <input type="range" class="slider-input" min="-3" max="5" step="1" [(ngModel)]="nodeDelta" (input)="updateScenario()">
          </div>

          <div class="control-group">
            <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; color: var(--text-primary);">
              <input type="checkbox" [(ngModel)]="armMigration" (change)="updateScenario()">
              Simulate ARM Graviton Migration (21% Savings)
            </label>
          </div>

          <div style="background-color: var(--bg-input); padding: 16px; border-radius: var(--radius); font-family: var(--font-mono); font-size: 13px; display: flex; flex-direction: column; gap: 8px; border: 1px solid var(--border-color);">
            <div>SLA Breach Risk: <span style="color: var(--accent-green)">{{ riskBadge }}</span></div>
            <div>Simulated Health Score: <strong>{{ simulatedHealth }}</strong></div>
            <div>Monthly Cost Delta: <strong style="color: var(--accent-cyan)">-$248.00 (-24.3%)</strong></div>
          </div>
        </div>

        <!-- Simulation Trajectory Chart Panel -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">What-If Workload Capacity Trajectory</h3>
            <span class="metric-badge badge-success">Monte Carlo / Holt-Winters Sandbox</span>
          </div>

          <div class="chart-container">
            <canvas #simulationCanvas></canvas>
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
            Scenario Sandbox Agent (Monte Carlo Simulator)
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.1); border: 1px dashed var(--accent-green); border-radius: 6px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green);">
            MCP: simulate_scenario
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
      height: 280px;
      width: 100%;
    }
  `]
})
export class SimulationComponent implements OnInit, AfterViewInit {
  @ViewChild('simulationCanvas') simulationCanvas!: ElementRef;

  trafficSurge = 1.5;
  nodeDelta = -1;
  armMigration = true;
  riskBadge = 'LOW';
  simulatedHealth = 88.0;

  simulationChart: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {}

  ngAfterViewInit() {
    setTimeout(() => {
      this.initChart();
    }, 100);
  }

  initChart() {
    if (typeof Chart === 'undefined' || !this.simulationCanvas) return;
    const ctx = this.simulationCanvas.nativeElement.getContext('2d');

    const labels = Array.from({ length: 14 }, (_, i) => `Day ${i + 1}`);
    const baseline = Array.from({ length: 14 }, (_, i) => 45 + i * 1.2);
    const surge = baseline.map(v => Math.min(100, v * this.trafficSurge));

    this.simulationChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'Baseline Forecast', data: baseline, borderColor: '#94a3b8', borderWidth: 2, borderDash: [4, 4], pointRadius: 0 },
          { label: 'Simulated Surge Trajectory', data: surge, borderColor: '#06b6d4', borderWidth: 3, tension: 0.3 }
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

  updateScenario() {
    if (!this.simulationChart) return;
    const mult = Number(this.trafficSurge);
    const baseline = Array.from({ length: 14 }, (_, i) => 45 + i * 1.2);
    const surge = baseline.map(v => Math.min(100, v * mult));

    this.simulationChart.data.datasets[1].data = surge;
    this.simulationChart.update();

    if (mult > 2.2) {
      this.riskBadge = 'CRITICAL';
      this.simulatedHealth = 62.0;
    } else if (mult > 1.8) {
      this.riskBadge = 'HIGH';
      this.simulatedHealth = 74.5;
    } else {
      this.riskBadge = 'LOW';
      this.simulatedHealth = 88.0;
    }
  }
}
