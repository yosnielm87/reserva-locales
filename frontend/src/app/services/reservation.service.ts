import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ReservationCreate, ReservationOut, ReservationWithLocale } from '../models/reservation.model';

@Injectable({ providedIn: 'root' })
export class ReservationService {
  private readonly api = 'http://localhost:8000/api/reservations';

  constructor(private http: HttpClient) { }

  create(data: ReservationCreate): Observable<ReservationOut> {
    return this.http.post<ReservationOut>(this.api, data);
  }

  myReservations(): Observable<ReservationOut[]> {
    return this.http.get<ReservationOut[]>(`${this.api}/my`);
  }

  getPendingWithLocale(): Observable<ReservationWithLocale[]> {
    return this.http.get<ReservationWithLocale[]>(`${this.api}/admin/reservations/pending`);
  }

  upcoming(userId: string): Observable<ReservationOut[]> {
    // usamos /my que YA existe y filtra por fecha
    return this.http.get<ReservationOut[]>(`${this.api}/my`);
  }

  history(userId: string): Observable<ReservationOut[]> {
    // si querés histórico, creá /my/history o filtrá del mismo /my
    return this.http.get<ReservationOut[]>(`${this.api}/my/history`);
  }

  cancel(id: string): Observable<void> {
    return this.http.delete<void>(`${this.api}/${id}`);
  }
}