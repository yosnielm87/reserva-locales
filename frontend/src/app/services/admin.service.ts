import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({ providedIn: 'root' })
export class AdminService {
    private api = 'http://localhost:8000/api/admin';
    constructor(private http: HttpClient) {}
    getConflicts(): Observable<any[]> {
        return this.http.get<any[]>(`${this.api}/conflicts`);
    }
    resolve(reservationId: string, priority: number, status: string): Observable<any> {
    return this.http.post<any>(`${this.api}/resolve`, {
        reservationId,
        priority,
        status
    });
    }
}