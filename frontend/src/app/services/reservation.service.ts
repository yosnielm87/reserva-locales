import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

/* ---------- interfaces ---------- */
export interface Reservation {
  id: string;
  locale_id: string;
  user_id: string;
  start_dt: string;
  end_dt: string;
  motive: string;
  status: 'pending' | 'approved' | 'rejected';
  priority?: number;
}

export interface ReservationCreate {
  locale_id: string;
  start_dt: string;
  end_dt: string;
  motive: string;
}

/** ➜ Nueva interfaz: incluye el nombre del local */
export interface ReservationWithLocale extends Reservation {
  locale_name: string;
}

@Injectable({ providedIn: 'root' })
export class ReservationService {
  private readonly api = 'http://localhost:8000/api/reservations';

  constructor(private http: HttpClient) {}

  /** Crear una reserva */
  create(data: ReservationCreate): Observable<Reservation> {
    return this.http.post<Reservation>(this.api, data);
  }

  /** Listar reservas del usuario logueado */
  myReservations(): Observable<Reservation[]> {
    return this.http.get<Reservation[]>(`${this.api}/my`);
  }

  /** ➜ Listar reservas PENDIENTES con nombre de local (para admin) */
  getPendingWithLocale(): Observable<ReservationWithLocale[]> {
    return this.http.get<ReservationWithLocale[]>(`${this.api}/admin/reservations/pending`);
  }
}