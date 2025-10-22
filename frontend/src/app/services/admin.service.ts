import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map, of } from 'rxjs';
import { ReservationOut, ReservationWithLocale, ReservationFull } from '../models/reservation.model';

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
  getPendingReservations(): Observable<ReservationFull[]> {
    return this.http.get<ReservationFull[]>(`${this.api}/reservations/pending`);
  }

  /** Aprobar / Rechazar */
  setReservationStatus(id: string, status: 'approved' | 'rejected'): Observable<ReservationOut> {
    return this.http.patch<ReservationOut>(`${this.api}/reservations/${id}/status`, { status });
  }

  /** Listar reservas pendientes con nombre del locale */
  getPendingWithLocale(): Observable<ReservationWithLocale[]> {
    return this.http.get<ReservationWithLocale[]>(`${this.api}/reservations/pending`);
  }

  /**
   * Obtiene reservas históricas (approved o cancelled) aplicando filtros de fecha.
   * IMPORTANTE: Este método construye los query parameters para evitar el error 404
   * que tenías anteriormente, ya que tu backend espera las fechas como filtros.
   * * @param start Fecha de inicio (string ISO 8601 o vacío)
   * @param end Fecha de fin (string ISO 8601 o vacío)
   */
  getHistoryWithLocale(start: string, end: string): Observable<ReservationWithLocale[]> {
    let params = new HttpParams();

    // 1. Añade los parámetros de fecha
    if (start) {
      params = params.set('start_date', start);
    }
    if (end) {
      params = params.set('end_date', end);
    }

    // 2. Llama al endpoint e incluye el tipado explícito en el map
    return this.http.get<ReservationWithLocale[]>(`${this.api}/history`, { params })
      .pipe(
        // FIX: Tipado explícito de 'data' para resolver TS7006
        map((data: ReservationWithLocale[]) => {
            console.log(`[AdminService] Datos recibidos del historial:`, data);
            return data || [];
        })
      );
  }
}