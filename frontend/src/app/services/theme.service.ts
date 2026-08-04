import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private isDarkSubject = new BehaviorSubject<boolean>(true);
  public isDark$ = this.isDarkSubject.asObservable();

  constructor() {
    const saved = localStorage.getItem('themePreference');
    if (saved === 'light') {
      this.setTheme(false);
    } else {
      this.setTheme(true);
    }
  }

  toggleTheme(): void {
    this.setTheme(!this.isDarkSubject.value);
  }

  private setTheme(isDark: boolean): void {
    this.isDarkSubject.next(isDark);
    if (isDark) {
      document.body.classList.remove('light-theme');
      localStorage.setItem('themePreference', 'dark');
    } else {
      document.body.classList.add('light-theme');
      localStorage.setItem('themePreference', 'light');
    }
  }
}
