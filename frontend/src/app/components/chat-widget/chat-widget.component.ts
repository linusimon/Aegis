import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { UserSession } from '../../services/auth.service';

export interface ChatMessage {
  sender: 'user' | 'agent';
  text: string;
  time: string;
}

@Component({
  selector: 'app-chat-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-widget-fab" (click)="toggleChat()">
      <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>
    </div>

    <div class="chat-popup-window" [class.open]="isOpen">
      <div class="chat-popup-header">
        <div>
          <div class="chat-popup-title">Aegis AI Infrastructure Assistant</div>
          <div style="font-size: 10px; color: var(--accent-green);">● Online (LangGraph + RAG Playbooks)</div>
        </div>
        <button class="btn-close-chat" (click)="toggleChat()">✕</button>
      </div>

      <div class="chat-popup-body">
        <div *ngFor="let msg of messages" class="message-bubble" [class.user-message]="msg.sender === 'user'" [class.assistant-message]="msg.sender === 'agent'">
          <div class="bubble-text">{{ msg.text }}</div>
          <div style="font-size: 9px; opacity: 0.7; margin-top: 4px; text-align: right;">{{ msg.time }}</div>
        </div>
        <div *ngIf="loading" style="font-size: 11px; color: var(--text-muted); font-style: italic;">
          AI Agent is analyzing telemetry & RAG playbooks...
        </div>
      </div>

      <div class="chat-chips-row">
        <button class="chat-chip" (click)="sendChip('What is the peak CPU forecast for Node-01?')">📊 Node-01 Peak CPU</button>
        <button class="chat-chip" (click)="sendChip('How can we cut cloud costs by 20%?')">💡 20% Cost Reduction</button>
        <button class="chat-chip" (click)="sendChip('Show SLA time-to-exhaustion risks')">⚠️ SLA Exhaustion Risks</button>
      </div>

      <div class="chat-popup-footer">
        <input type="text" [(ngModel)]="inputMsg" (keyup.enter)="sendMessage()" placeholder="Ask about capacity, FinOps, risk..." class="chat-input" />
        <button class="btn-primary" (click)="sendMessage()">Send</button>
      </div>
    </div>
  `,
  styles: [`
    .chat-widget-fab {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 52px;
      height: 52px;
      background-color: var(--accent-cyan);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 100;
      transition: transform 0.15s ease;
    }
    .chat-widget-fab:hover {
      transform: scale(1.05);
    }
    .chat-widget-fab svg {
      width: 24px;
      height: 24px;
      fill: #0f172a;
    }
    .chat-popup-window {
      position: fixed;
      bottom: 88px;
      right: 24px;
      width: 380px;
      height: 520px;
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      display: none;
      flex-direction: column;
      z-index: 100;
    }
    .chat-popup-window.open {
      display: flex;
    }
    .chat-popup-header {
      padding: 14px 18px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-sidebar);
    }
    .chat-popup-title {
      font-family: var(--font-headline);
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .btn-close-chat {
      background: none;
      border: none;
      color: var(--text-secondary);
      font-size: 16px;
      cursor: pointer;
    }
    .chat-popup-body {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .message-bubble {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.45;
    }
    .assistant-message {
      background-color: var(--bg-input);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      align-self: flex-start;
    }
    .user-message {
      background-color: var(--accent-cyan);
      color: #0f172a;
      font-weight: 500;
      align-self: flex-end;
    }
    .chat-chips-row {
      display: flex;
      gap: 6px;
      padding: 8px 16px;
      overflow-x: auto;
      border-top: 1px solid var(--border-color);
    }
    .chat-chip {
      background: var(--bg-input);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      white-space: nowrap;
    }
    .chat-chip:hover {
      border-color: var(--accent-cyan);
      color: var(--text-primary);
    }
    .chat-popup-footer {
      padding: 12px 16px;
      border-top: 1px solid var(--border-color);
      display: flex;
      gap: 8px;
    }
  `]
})
export class ChatWidgetComponent {
  @Input() user: UserSession | null = null;

  isOpen = false;
  inputMsg = '';
  loading = false;

  messages: ChatMessage[] = [
    { sender: 'agent', text: 'Hello! I am your AI Infrastructure Capacity Advisor. How can I assist with your server telemetry or FinOps strategy today?', time: 'Just now' }
  ];

  constructor(private apiService: ApiService) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  sendChip(prompt: string) {
    this.inputMsg = prompt;
    this.sendMessage();
  }

  sendMessage() {
    if (!this.inputMsg.trim() || this.loading) return;
    const text = this.inputMsg.trim();
    this.inputMsg = '';

    this.messages.push({ sender: 'user', text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    this.loading = true;

    const role = this.user?.role || 'user';
    this.apiService.sendAgentChat(text, role).subscribe({
      next: (res) => {
        this.loading = false;
        const agentText = res.response || res.message || 'Agent query processed successfully.';
        this.messages.push({ sender: 'agent', text: agentText, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
      },
      error: () => {
        this.loading = false;
        this.messages.push({ sender: 'agent', text: 'Sorry, I encountered an error reaching the agent server.', time: 'Now' });
      }
    });
  }
}
