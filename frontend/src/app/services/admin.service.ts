import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Reservation } from './reservation.service';
import { ReservationWithLocale } from '../services/reservation.service'; // importas el tipo

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

    /** Listar reservas pendientes */
    getPendingReservations(): Observable<Reservation[]> {
        return this.http.get<Reservation[]>(`${this.api}/reservations/pending`);
    }

    /** Aprobar / Rechazar */
    setReservationStatus(id: string, status: 'approved' | 'rejected'): Observable<any> {
        return this.http.patch(`${this.api}/reservations/${id}/status`, status);
    }

    getPendingWithLocale(): Observable<ReservationWithLocale[]> {
        return this.http.get<ReservationWithLocale[]>(`${this.api}/reservations/pending`);
    }
}