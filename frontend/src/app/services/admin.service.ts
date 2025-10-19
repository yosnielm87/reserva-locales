import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ReservationOut, ReservationWithLocale } from '../models/reservation.model';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private api = 'http://localhost:8000/api/admin';

  constructor(private http: HttpClient) {}

  getConflicts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/conflicts`);
  }

  resolve(reservationId: string, priority: number, status: string): Observable<any> {
    return this.http.post<any>(`${this.api}/resolve`, { reservationId, priority, status });
  }

  /** Listar reservas pendientes (sin imagen) */
  getPendingReservations(): Observable<ReservationOut[]> {
    return this.http.get<ReservationOut[]>(`${this.api}/reservations/pending`);
  }

  /** Aprobar / Rechazar */
  setReservationStatus(id: string, status: 'approved' | 'rejected'): Observable<ReservationOut> {
    return this.http.patch<ReservationOut>(`${this.api}/reservations/${id}/status`, { status });
  }

  /** Listar reservas pendientes con nombre del locale */
  getPendingWithLocale(): Observable<ReservationWithLocale[]> {
    return this.http.get<ReservationWithLocale[]>(`${this.api}/reservations/pending`);
  }
}