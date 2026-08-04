import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-agent-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="agent-modal-overlay open" (click)="close.emit()">
      <div class="agent-modal-content" (click)="$event.stopPropagation()">
        <div class="agent-modal-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="pulse-indicator"></span>
            <span class="node-title">LangGraph Multi-Agent Architecture Topology</span>
          </div>
          <button class="btn-nav-action" (click)="close.emit()">✕ Close</button>
        </div>

        <div class="agent-modal-body">
          <div class="graph-canvas-container">
            <!-- Central Supervisor Node -->
            <div class="agent-node node-supervisor">
              <span class="node-title">Supervisor Orchestrator Hub</span>
              <span class="node-role">LangGraph Conditional State Router</span>
              <span class="node-badge">Gemini AI / LiteLLM</span>
            </div>

            <!-- Worker Nodes Row -->
            <div style="display: flex; gap: 16px; flex-wrap: wrap; justify-content: center;" class="agent-workflow-row">
              <div class="agent-node">
                <span class="node-title">Data Agent</span>
                <span class="node-role">Metric Validation</span>
                <span class="node-mcp">🛠️ MCP: insert_metrics</span>
              </div>

              <div class="agent-node">
                <span class="node-title">Forecasting Agent</span>
                <span class="node-role">Holt-Winters Ensemble</span>
                <span class="node-mcp">🛠️ MCP: save_forecast</span>
              </div>

              <div class="agent-node">
                <span class="node-title">Risk Agent</span>
                <span class="node-role">SLA & TTE Analysis</span>
                <span class="node-mcp">🛠️ MCP: risk_assessment</span>
              </div>

              <div class="agent-node">
                <span class="node-title">FinOps Agent</span>
                <span class="node-role">RAG Right-Sizing</span>
                <span class="node-mcp">🛠️ MCP: query_playbook</span>
              </div>

              <div class="agent-node">
                <span class="node-title">Scenario Agent</span>
                <span class="node-role">What-If Sandbox</span>
                <span class="node-mcp">🛠️ MCP: simulate_scenario</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .agent-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.85);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .agent-modal-content {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      width: 840px;
      max-width: 90vw;
      overflow: hidden;
    }
    .agent-modal-header {
      padding: 18px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .agent-modal-body {
      padding: 24px;
      max-height: 80vh;
      overflow-y: auto;
    }
    .graph-canvas-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 28px;
    }
    .agent-node {
      background-color: var(--bg-sidebar);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 140px;
      text-align: center;
    }
    .node-supervisor {
      background: var(--bg-card);
      border: 2px solid var(--accent-cyan);
      width: 320px;
    }
    .node-title {
      font-family: var(--font-headline);
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .node-role {
      font-size: 11px;
      color: var(--text-secondary);
    }
    .node-badge {
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--accent-cyan);
      background-color: rgba(6, 182, 212, 0.12);
      padding: 2px 8px;
      border-radius: 4px;
      margin-top: 6px;
    }
    .node-mcp {
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--accent-green);
      margin-top: 6px;
    }
  `]
})
export class AgentModalComponent {
  @Output() close = new EventEmitter<void>();
}
