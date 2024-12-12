import { inject, Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { catchError, Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly tokenKey = 'auth_token';

  login(username: string, password: string): Observable<{ token: string } | { error: string }> {
    return this.api
      .post<{ token: string } | { error: string }>('login', { username, password })
      .pipe(
        tap((response) => {
          if ('token' in response) this.setToken(response.token);
        }),
        catchError((error) => {
          console.error('Login error:', error);
          throw error;
        }),
      );
  }

  register(username: string, password: string): Observable<{ username: string } | { errors: any }> {
    return this.api
      .post<{ username: string } | { errors: any }>('register', { username, password })
      .pipe(
        catchError((error) => {
          console.error('Register error:', error);
          throw error;
        }),
      );
  }

  logout(): Observable<{ message: string } | { error: string }> {
    return this.api.post<{ message: string }>('logout', {}).pipe(
      tap(() => localStorage.removeItem(this.tokenKey)),
      catchError((error) => {
        console.error('Logout error:', error);
        throw error;
      }),
    );
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  private setToken(token: string): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.setItem(this.tokenKey, token);
  }
}
