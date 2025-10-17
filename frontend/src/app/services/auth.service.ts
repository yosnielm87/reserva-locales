// auth.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, EMPTY, Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {

  private readonly api = 'http://localhost:8000/api/auth';
  private readonly http = inject(HttpClient);

  private user$ = new BehaviorSubject<{email: string; full_name: string; role: string} | null>(null);

  /* ---------- API calls ---------- */
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

  register(dto: {email: string; password: string; full_name: string}) {
    return this.http.post<{access_token: string; token_type: string}>(`${this.api}/register`, dto);
  }

  getMe() {
    return this.http.get<{email: string; full_name: string; role: string}>(`${this.api}/me`);
  }

  logout(): void {
    localStorage.removeItem('token');
    this.clearUser();
  }

  /* ---------- getters ---------- */
  get token(): string | null {
    return localStorage.getItem('token');
  }

  isAdmin(): boolean {
    if (!this.token) return false;
    const payload = JSON.parse(atob(this.token.split('.')[1]));
    return payload.role === 'admin';
  }

  /* ---------- user subject ---------- */
  setUser(u: {email: string; full_name: string; role: string}) { this.user$.next(u); }
  getUser() { return this.user$.asObservable(); }
  clearUser() { this.user$.next(null); }

  /* ---------- init session ---------- */
  initSession() {
    if (!this.token) {                  // sin token → nada que hacer
      this.clearUser();
      return EMPTY;
    }
    // intentamos recuperar al usuario
    return this.getMe().pipe(
      tap(user => this.setUser(user)),  // éxito → guardamos
      catchError(() => {                // token inválido / expirado
        this.logout();                  // limpiamos todo
        return EMPTY;                   // devolvemos observable vacío
      })
    );
  }
}