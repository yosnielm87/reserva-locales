import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { LocaleOut } from '../models/locale.model';

@Injectable({
  providedIn: 'root'
})
export class LocaleAdminService {
  private api = 'http://localhost:8000/api/admin/locales';

  constructor(private http: HttpClient) {}

  // CRUD
  list(): Observable<LocaleOut[]> {
    return this.http.get<LocaleOut[]>(this.api);
  }

  create(dto: FormData): Observable<LocaleOut> {
    return this.http.post<LocaleOut>(this.api, dto);
  }

  update(id: string, dto: FormData): Observable<LocaleOut> {
    return this.http.patch<LocaleOut>(`${this.api}/${id}`, dto);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.api}/${id}`);
  }
}
