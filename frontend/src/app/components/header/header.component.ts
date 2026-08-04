import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserSession } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="top-navbar">
      <div>
        <h1 class="page-title">{{ titleMap[activeTab] || 'Dashboard' }}</h1>
      </div>

      <div class="top-navbar-actions">
        <div class="system-status-indicator">
          <span class="pulse-dot"></span>
          <span>MCP SQLite + LangGraph Active</span>
        </div>

        <button class="btn-nav-action" (click)="openAgentModal.emit()">
          🤖 View Agent Graph
        </button>

        <div class="export-btn-group">
          <button class="btn-nav-action" (click)="exportReport('html')">📥 HTML Report</button>
          <button class="btn-nav-action btn-pdf" (click)="exportReport('pdf')">📄 PDF Report</button>
        </div>

        <button class="btn-nav-action" (click)="toggleTheme.emit()">
          {{ isDark ? '☀️ Light' : '🌙 Dark' }}
        </button>

        <div class="user-profile-badge">
          <span>👤</span>
          <span>{{ user ? (user.role | uppercase) + ' (' + user.username + ')' : 'Guest (Read-Only)' }}</span>
          <button *ngIf="user" class="btn-logout" (click)="logout.emit()">Sign Out</button>
          <button *ngIf="!user" class="btn-nav-action" (click)="openLogin.emit()" style="padding: 2px 8px; font-size: 11px;">Sign In</button>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .export-btn-group {
      display: flex;
      align-items: center;
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid var(--border-color);
    }
    .export-btn-group .btn-nav-action {
      border: none;
      border-radius: 0;
    }
    .export-btn-group .btn-pdf {
      background: #0284c7;
      color: white;
    }
    .export-btn-group .btn-pdf:hover {
      background: #0369a1;
    }
  `]
})
export class HeaderComponent {
  @Input() activeTab: string = 'overview';
  @Input() isDark: boolean = true;
  @Input() user: UserSession | null = null;

  @Output() toggleTheme = new EventEmitter<void>();
  @Output() openLogin = new EventEmitter<void>();
  @Output() logout = new EventEmitter<void>();
  @Output() openAgentModal = new EventEmitter<void>();

  titleMap: Record<string, string> = {
    'overview': 'Overview Dashboard',
    'predictive': 'Predictive Engine (Time-Series Forecasting)',
    'finops': 'FinOps Optimization & Right-Sizing Advisory',
    'simulation': 'What-If Capacity Stress Testing Sandbox',
    'risk': 'Risk & Reliability Operations Center'
  };

  exportReport(format: string = 'html') {
    window.open(`http://localhost:8000/api/export-report?format=${format}`, '_blank');
  }
}
