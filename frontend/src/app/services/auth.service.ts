import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
@Injectable({ providedIn: 'root' })
export class AuthService {
    private api = 'http://localhost:8000/api/auth';
    constructor(private http: HttpClient) {}
    login(email: string, password: string): Observable<{access_token: string}> {
        const form = new FormData();
        form.append('username', email);
        form.append('password', password);
        return this.http.post<{access_token: string}>(`${this.api}/login`, form, { responseType: 'json' })
        .pipe(tap(res => localStorage.setItem('token', res.access_token)));
    }
    register(email: string, password: string, fullName: string) {
        return this.http.post(`${this.api}/register`, {email, password, full_name: fullName});
    }
    logout() { 
        localStorage.removeItem('token'); 
    }
    get token(): string | null { 
        return localStorage.getItem('token'); 
    }
    isAdmin(): boolean {
        const payload = JSON.parse(atob((this.token || '').split('.')[1]));
        return payload.role === 'admin';
    }
}