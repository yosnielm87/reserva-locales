// auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = 'http://localhost:8000/api/auth';
  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<{ access_token: string }> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http.post<{ access_token: string }>(
      `${this.api}/login`,
      body.toString(),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ).pipe(tap(res => localStorage.setItem('token', res.access_token)));
  }

  register(dto: {email: string, password: string, full_name: string}) {
    return this.http.post<{access_token: string, token_type: string}>
          ('/api/auth/register', dto);
 }

  logout(): void {
    localStorage.removeItem('token');
  }

  get token(): string | null {
    return localStorage.getItem('token');
  }

  isAdmin(): boolean {
    if (!this.token) return false;
    const payload = JSON.parse(atob(this.token.split('.')[1]));
    return payload.role === 'admin';
  }
}