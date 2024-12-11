import { inject, Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { catchError, Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly tokenKey = 'auth_token';

  login(email: string, password: string): Observable<{ token: string }> {
    return this.api.post<{ token: string }>('auth/login', { email, password }).pipe(
      tap((response) => this.setToken(response.token)),
      catchError((error) => {
        console.error('Login error:', error);
        throw error;
      }),
    );
  }

  register(email: string, password: string): Observable<{ token: string }> {
    return this.api.post<{ token: string }>('auth/register', { email, password }).pipe(
      tap((response) => this.setToken(response.token)),
      catchError((error) => {
        console.error('Register error:', error);
        throw error;
      }),
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private setToken(token: string): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.setItem(this.tokenKey, token);
  }

  private getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}