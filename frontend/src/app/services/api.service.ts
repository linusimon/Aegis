import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  getMetrics(limit = 15): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/monitoring/metrics?limit=${limit}`);
  }

  getHistoricalTrend(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/monitoring/historical-trend`);
  }

  generateSyntheticPreset(preset: string, numNodes = 3, days = 30): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/generate-synthetic-metrics?preset=${preset}&num_nodes=${numNodes}&days=${days}`, {});
  }

  getForecast(nodeId = 'Node-01', horizonDays = 7): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/forecast/${nodeId}?horizon_days=${horizonDays}`);
  }

  getRightSizingAdvisory(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/advisory/right-sizing`);
  }

  computeWhatIf(payload: { workload_pct: number; duration_days: number; capacity_delta_nodes: number; arm_migration: boolean }): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/whatif`, payload);
  }

  getRiskAssessment(cpuLimit = 85, memLimit = 90): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/v1/advisory/risk-assessment?cpu_limit=${cpuLimit}&mem_limit=${memLimit}`);
  }

  sendAgentChat(message: string, userRole = 'user'): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/v1/agents/chat`, { message, user_role: userRole });
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/auth/login`, { username, password });
  }
}
