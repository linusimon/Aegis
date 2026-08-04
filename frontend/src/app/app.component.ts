import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { HeaderComponent } from './components/header/header.component';
import { LoginModalComponent } from './components/login-modal/login-modal.component';
import { ChatWidgetComponent } from './components/chat-widget/chat-widget.component';
import { AgentModalComponent } from './components/agent-modal/agent-modal.component';

import { OverviewComponent } from './pages/overview/overview.component';
import { PredictiveComponent } from './pages/predictive/predictive.component';
import { FinopsComponent } from './pages/finops/finops.component';
import { SimulationComponent } from './pages/simulation/simulation.component';
import { RiskComponent } from './pages/risk/risk.component';

import { AuthService, UserSession } from './services/auth.service';
import { ThemeService } from './services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    SidebarComponent,
    HeaderComponent,
    LoginModalComponent,
    ChatWidgetComponent,
    AgentModalComponent,
    OverviewComponent,
    PredictiveComponent,
    FinopsComponent,
    SimulationComponent,
    RiskComponent
  ],
  template: `
    <div class="app-container">
      <app-sidebar [activeTab]="activeTab" (tabChange)="onTabChange($event)"></app-sidebar>

      <div class="main-wrapper">
        <app-header
          [activeTab]="activeTab"
          [isDark]="isDark"
          [user]="currentUser"
          (toggleTheme)="toggleTheme()"
          (openLogin)="showLoginModal = true"
          (logout)="logout()"
          (openAgentModal)="showAgentModal = true"
        ></app-header>

        <main class="content-area">
          <app-overview *ngIf="activeTab === 'overview'"></app-overview>
          <app-predictive *ngIf="activeTab === 'predictive'"></app-predictive>
          <app-finops *ngIf="activeTab === 'finops'"></app-finops>
          <app-simulation *ngIf="activeTab === 'simulation'"></app-simulation>
          <app-risk *ngIf="activeTab === 'risk'"></app-risk>
        </main>
      </div>

      <app-chat-widget [user]="currentUser"></app-chat-widget>
      <app-login-modal *ngIf="showLoginModal" (close)="showLoginModal = false"></app-login-modal>
      <app-agent-modal *ngIf="showAgentModal" (close)="showAgentModal = false"></app-agent-modal>
    </div>
  `
})
export class AppComponent implements OnInit {
  activeTab = 'overview';
  isDark = true;
  currentUser: UserSession | null = null;
  showLoginModal = false;
  showAgentModal = false;

  constructor(private authService: AuthService, private themeService: ThemeService) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.themeService.isDark$.subscribe(isDark => {
      this.isDark = isDark;
    });
  }

  onTabChange(tab: string) {
    this.activeTab = tab;
  }

  toggleTheme() {
    this.themeService.toggleTheme();
  }

  logout() {
    this.authService.logout();
  }
}
