import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({ providedIn: 'root' })
export class ReservationService {
private api = 'http://localhost:8000/api/reservations';
constructor(private http: HttpClient) {}
create(data: any): Observable<any> {
  return this.http.post<any>(`${this.api}`, data);
}

myReservations(): Observable<any[]> {
  return this.http.get<any[]>(`${this.api}/my`);
}
}