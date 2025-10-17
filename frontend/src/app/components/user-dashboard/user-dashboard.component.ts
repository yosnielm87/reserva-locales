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
        auth = inject(AuthService);
        user$ = this.auth.getUser();   // Observable con los datos del usuario
        reservationSvc = inject(ReservationService);
        localeSvc = inject(LocaleService);
        locales: any[] = [];
        reservations: any[] = [];
    ngOnInit() {
        this.localeSvc.list().subscribe(data => this.locales = data);
        this.reservationSvc.myReservations().subscribe(data => this.reservations = data);
    }
    onReserve(localeId: string, start: string, end: string, motive: string) {
        this.reservationSvc.create({ locale_id: localeId, start_dt: start, end_dt: end, motive })
        .subscribe(() => {
        alert('Reserva solicitada');
        this.ngOnInit();
    });
    }
    logout() {
        this.auth.logout();
        window.location.href = '/login';
    }
}