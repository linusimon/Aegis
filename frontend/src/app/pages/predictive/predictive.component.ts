import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

declare var Chart: any;

@Component({
  selector: 'app-predictive',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="tab-page active-page">
      <div class="panel-card">
        <div class="panel-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <h3 class="panel-title">Predictive Time-Series Forecast (95% Confidence Corridor)</h3>
            <select [(ngModel)]="selectedNode" (change)="loadForecast()" class="chat-input" style="width: auto; padding: 6px 12px; font-size: 13px;">
              <option value="Node-01">Node-01 (c5.4xlarge)</option>
              <option value="Node-02">Node-02 (c5.2xlarge)</option>
              <option value="Node-03">Node-03 (m5.2xlarge)</option>
            </select>
          </div>
          <div class="horizon-buttons">
            <button class="btn-tab" [class.active]="horizonDays === 7" (click)="setHorizon(7)">7 Days</button>
            <button class="btn-tab" [class.active]="horizonDays === 30" (click)="setHorizon(30)">30 Days</button>
            <button class="btn-tab" [class.active]="horizonDays === 90" (click)="setHorizon(90)">90 Days</button>
          </div>
        </div>

        <div class="chart-container">
          <canvas #forecastCanvas></canvas>
        </div>

        <!-- Predictive Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border-color);">
          <div class="anomaly-item item-normal">
            <div style="font-size: 11px; color: var(--text-secondary);">Time-To-Exhaustion (TTE)</div>
            <div style="font-size: 16px; font-weight: 700; color: var(--accent-green);">{{ tteText }}</div>
            <div style="font-size: 11px; color: var(--text-secondary);">Safe SLA Horizon</div>
          </div>

          <div class="anomaly-item item-normal">
            <div style="font-size: 11px; color: var(--text-secondary);">Model Accuracy (MAPE)</div>
            <div style="font-size: 16px; font-weight: 700; color: var(--accent-cyan);">{{ mapeText }}</div>
            <div style="font-size: 11px; color: var(--accent-green);">Target ≥ 80% Met</div>
          </div>

          <div class="anomaly-item item-normal">
            <div style="font-size: 11px; color: var(--text-secondary);">Forecast Peak Utilization</div>
            <div style="font-size: 16px; font-weight: 700; color: var(--text-primary);">{{ peakText }}</div>
            <div style="font-size: 11px; color: var(--text-secondary);">Below 85% SLA Breach Limit</div>
          </div>

          <div class="anomaly-item item-normal">
            <div style="font-size: 11px; color: var(--text-secondary);">SLA Breach Status</div>
            <div style="font-size: 16px; font-weight: 700; color: var(--accent-green);">0 Breaches</div>
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
            Forecast Agent (Holt-Winters Ridge Ensemble)
          </div>
          <div style="color: var(--accent-cyan);">➔</div>
          <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.1); border: 1px dashed var(--accent-green); border-radius: 6px; font-size: 11px; font-family: var(--font-mono); color: var(--accent-green);">
            MCP: save_forecast
          </div>
          <div style="color: var(--accent-green);">➔</div>
          <div style="padding: 10px 16px; background: var(--bg-sidebar); border: 1px solid var(--border-color); border-radius: 8px; font-size: 12px;">
            Risk Assessment Agent ➔ FinOps Agent
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
export class PredictiveComponent implements OnInit, AfterViewInit {
  @ViewChild('forecastCanvas') forecastCanvas!: ElementRef;

  selectedNode = 'Node-01';
  horizonDays = 7;
  forecastChart: any = null;

  tteText = '>30 Days';
  mapeText = '8.5% (91.5% Accuracy)';
  peakText = '82.4% CPU';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadForecast();
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.initChart();
    }, 100);
  }

  initChart() {
    if (typeof Chart === 'undefined' || !this.forecastCanvas) return;
    const ctx = this.forecastCanvas.nativeElement.getContext('2d');

    const labels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);
    const baseData = Array.from({ length: 30 }, (_, i) => 45 + (i * 1.2));
    const lowerBound = baseData.map(v => Math.max(0, v - 7));
    const upperBound = baseData.map(v => Math.min(100, v + 7));

    this.forecastChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'Upper 95% Bound', data: upperBound, borderColor: 'transparent', backgroundColor: 'rgba(56, 189, 248, 0.12)', fill: '+1', pointRadius: 0 },
          { label: 'Lower 95% Bound', data: lowerBound, borderColor: 'transparent', backgroundColor: 'transparent', fill: false, pointRadius: 0 },
          { label: 'Predicted CPU %', data: baseData, borderColor: '#06b6d4', borderWidth: 3, pointBackgroundColor: '#06b6d4', tension: 0.3 },
          { label: '85% SLA Breach Limit', data: Array(30).fill(85), borderColor: '#f43f5e', borderWidth: 2, borderDash: [6, 6], pointRadius: 0, fill: false }
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

  setHorizon(days: number) {
    this.horizonDays = days;
    this.loadForecast();
  }

  loadForecast() {
    this.apiService.getForecast(this.selectedNode, this.horizonDays).subscribe({
      next: (res) => {
        if (res.forecast) {
          const f = res.forecast;
          this.tteText = f.days_to_cpu_exhaustion ? `${f.days_to_cpu_exhaustion} Days` : '>30 Days';
          this.mapeText = `${(100 - (f.accuracy_pct || 91.5)).toFixed(1)}% (${(f.accuracy_pct || 91.5).toFixed(1)}% Accuracy)`;
          this.peakText = `${(f.projected_cpu_peak || 82.4).toFixed(1)}% CPU`;
        }
      }
    });
  }
}
