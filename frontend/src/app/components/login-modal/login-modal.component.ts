import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <div class="brand-badge">Aegis AI</div>
          <h2>Authentication Required</h2>
          <p>Sign in to access cluster metrics, capacity forecasting, and FinOps actions.</p>
        </div>

        <form (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label>Username</label>
            <input type="text" [(ngModel)]="username" name="username" placeholder="admin or user" required class="input-field" />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input type="password" [(ngModel)]="password" name="password" placeholder="admin123 or user123" required class="input-field" />
          </div>

          <div *ngIf="errorMsg" class="error-msg">
            {{ errorMsg }}
          </div>

          <button type="submit" [disabled]="loading" class="btn-primary btn-block">
            {{ loading ? 'Authenticating...' : 'Sign In' }}
          </button>
        </form>

        <div class="quick-login">
          <span>Quick Demo Access:</span>
          <div class="quick-buttons">
            <button type="button" class="btn-secondary btn-sm" (click)="quickLogin('admin', 'admin123')">🔑 Admin Demo</button>
            <button type="button" class="btn-secondary btn-sm" (click)="quickLogin('user', 'user123')">👁️ Viewer Demo</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-lg);
      padding: 32px;
      width: 400px;
      box-shadow: var(--shadow-glass);
    }
    .brand-badge {
      display: inline-block;
      padding: 4px 10px;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      color: white;
      font-size: 11px;
      font-weight: 700;
      border-radius: 12px;
      margin-bottom: 8px;
    }
    .modal-header h2 {
      font-size: 20px;
      margin-bottom: 6px;
    }
    .modal-header p {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 20px;
    }
    .form-group {
      margin-bottom: 16px;
    }
    .form-group label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-secondary);
    }
    .input-field {
      width: 100%;
      padding: 10px 14px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
      font-family: inherit;
    }
    .btn-block {
      width: 100%;
      margin-top: 12px;
    }
    .error-msg {
      color: var(--accent-rose);
      font-size: 12px;
      margin-bottom: 10px;
    }
    .quick-login {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--border-glass);
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
    }
    .quick-buttons {
      display: flex;
      gap: 8px;
      justify-content: center;
      margin-top: 8px;
    }
    .btn-sm {
      font-size: 11px;
      padding: 6px 12px;
    }
  `]
})
export class LoginModalComponent {
  @Output() close = new EventEmitter<void>();

  username = '';
  password = '';
  loading = false;
  errorMsg = '';

  constructor(private authService: AuthService) {}

  onSubmit() {
    if (!this.username || !this.password) return;
    this.loading = true;
    this.errorMsg = '';

    this.authService.login(this.username, this.password).subscribe({
      next: (res) => {
        this.loading = false;
        if (res.status === 'success') {
          this.close.emit();
        } else {
          this.errorMsg = res.detail || 'Authentication failed.';
        }
      },
      error: () => {
        this.loading = false;
        this.errorMsg = 'Failed to connect to authentication server.';
      }
    });
  }

  quickLogin(user: string, pass: string) {
    this.username = user;
    this.password = pass;
    this.onSubmit();
  }
}
