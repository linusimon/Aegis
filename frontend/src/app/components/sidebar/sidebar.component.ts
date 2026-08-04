import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <aside class="sidebar">
      <div class="brand-header">
        <div class="brand-logo">AI</div>
        <div>
          <div class="brand-title">Aegis AI</div>
          <div class="brand-subtitle">Capacity Advisor</div>
        </div>
      </div>

      <ul class="nav-list">
        <li class="nav-item" [class.active]="activeTab === 'overview'">
          <button (click)="selectTab('overview')">
            <svg class="nav-icon" viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z"/></svg>
            Overview
          </button>
        </li>
        <li class="nav-item" [class.active]="activeTab === 'predictive'">
          <button (click)="selectTab('predictive')">
            <svg class="nav-icon" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
            Predictive Engine
          </button>
        </li>
        <li class="nav-item" [class.active]="activeTab === 'finops'">
          <button (click)="selectTab('finops')">
            <svg class="nav-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
            FinOps Optimization
          </button>
        </li>
        <li class="nav-item" [class.active]="activeTab === 'simulation'">
          <button (click)="selectTab('simulation')">
            <svg class="nav-icon" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
            What-If Simulation
          </button>
        </li>
        <li class="nav-item" [class.active]="activeTab === 'risk'">
          <button (click)="selectTab('risk')">
            <svg class="nav-icon" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 6h2v6h-2V7zm0 8h2v2h-2v-2z"/></svg>
            Risk & Reliability
          </button>
        </li>
      </ul>

      <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border-color);">
        <div style="display: flex; align-items: center; gap: 6px; font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">
          <span class="pulse-dot"></span>
          <span>MCP SSE Server Connected</span>
        </div>
      </div>
    </aside>
  `
})
export class SidebarComponent {
  @Input() activeTab: string = 'overview';
  @Output() tabChange = new EventEmitter<string>();

  selectTab(tab: string) {
    this.tabChange.emit(tab);
  }
}
