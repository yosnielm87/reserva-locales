//frontend/src/services/locale.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TimeSlot {
    start_dt: string; 
    end_dt: string;
}

export interface AvailabilityResponse {
    available: string[];
    occupied: string[];
}

@Injectable({ providedIn: 'root' })
export class LocaleService {
    private api = 'http://localhost:8000/api/locales';
    constructor(private http: HttpClient) { }

    list(): Observable<any[]> {
        return this.http.get<any[]>(this.api);
    }

    /**
     * Obtiene los horarios disponibles y ocupados para un local en una fecha específica.
     * @param localeId ID del local
     * @param dateStr Fecha a consultar en formato 'YYYY-MM-DD'
     */
    getAvailability(localeId: string, dateStr: string): Observable<AvailabilityResponse> {
        let params = new HttpParams();
        params = params.set('search_date', dateStr);

        return this.http.get<AvailabilityResponse>(
            `${this.api}/${localeId}/availability`, 
            { params: params }
        );
    }
}