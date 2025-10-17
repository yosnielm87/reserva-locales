import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ReservationService } from '../../services/reservation.service';
import { LocaleService } from '../../services/locale.service';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {
  private auth = inject(AuthService);
  private reservationSvc = inject(ReservationService);
  private localeSvc = inject(LocaleService);

  /* ---------- usuario ---------- */
  user$ = this.auth.getUser();          // para el template (async pipe)
  private get userSnap() { return (this.auth as any)['user$'].value; }

  /* ---------- datos ---------- */
  locales: any[] = [];
  reservations: any[] = [];

  ngOnInit(): void {
    /* si no hay usuario en memoria, lo recuperamos */
    if (!this.userSnap) {
      this.auth.initSession().subscribe();
    }

    /* cargamos listados */
    this.localeSvc.list().subscribe(data => this.locales = data);
    this.reservationSvc.myReservations().subscribe(data => this.reservations = data);
  }

  onReserve(localeId: string, start: string, end: string, motive: string): void {
    this.reservationSvc.create({ locale_id: localeId, start_dt: start, end_dt: end, motive })
      .subscribe(() => {
        alert('Reserva solicitada');
        this.ngOnInit();   // recargar lista
      });
  }

  logout(): void {
    this.auth.logout();
    window.location.href = '/login';
  }
}