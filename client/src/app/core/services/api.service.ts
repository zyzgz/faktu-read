import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly http = inject(HttpClient);

  private readonly baseUrl = 'http://127.0.0.1:8000/api';

  private getHttpOptions(body?: any) {
    const headers = new HttpHeaders();
    if (!(body instanceof FormData)) headers.set('Content-Type', 'application/json');

    return { headers };
  }

  get<T>(endpoint: string, params?: HttpParams, options?: any): Observable<any> {
    const defaultOptions = this.getHttpOptions();
    const mergedOptions = { ...defaultOptions, ...options, params };
    return this.http.get<T>(`${this.baseUrl}/${endpoint}`, mergedOptions);
  }

  post<T>(endpoint: string, body: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, body, this.getHttpOptions(body));
  }

  put<T>(endpoint: string, body: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}/${endpoint}`, body, this.getHttpOptions(body));
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}/${endpoint}`, this.getHttpOptions());
  }
}
