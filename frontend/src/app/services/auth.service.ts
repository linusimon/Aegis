import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface UserSession {
  username: string;
  role: 'admin' | 'user';
  token?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<UserSession | null>(null);
  public currentUser$: Observable<UserSession | null> = this.currentUserSubject.asObservable();

  constructor(private apiService: ApiService) {
    this.loadSession();
  }

  private loadSession(): void {
    const saved = localStorage.getItem('currentUser');
    if (saved) {
      try {
        const user = JSON.parse(saved);
        this.currentUserSubject.next(user);
      } catch (e) {
        localStorage.removeItem('currentUser');
      }
    }
  }

  public get currentUserValue(): UserSession | null {
    return this.currentUserSubject.value;
  }

  login(username: string, password: string): Observable<any> {
    return new Observable(observer => {
      this.apiService.login(username, password).subscribe({
        next: (res) => {
          if (res.status === 'success' && res.user) {
            localStorage.setItem('currentUser', JSON.stringify(res.user));
            this.currentUserSubject.next(res.user);
          }
          observer.next(res);
          observer.complete();
        },
        error: (err) => {
          observer.error(err);
        }
      });
    });
  }

  logout(): void {
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }
}
