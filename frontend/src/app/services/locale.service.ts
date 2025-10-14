import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({ providedIn: 'root' })
export class LocaleService {
private api = 'http://localhost:8000/api/locales';
constructor(private http: HttpClient) {}
list(): Observable<any[]> {
return this.http.get<any[]>(this.api);
}
}