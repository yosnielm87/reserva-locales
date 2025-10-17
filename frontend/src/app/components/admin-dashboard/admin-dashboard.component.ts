import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { AdminService } from '../../services/admin.service';
import { ReservationWithLocale } from '../../services/reservation.service'; // ← importamos el tipo

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  private auth = inject(AuthService);
  private adminSvc = inject(AdminService);

  /* snapshot del BehaviorSubject */
  private get userSnap() { return (this.auth as any)['user$'].value; }
  user$ = this.auth.getUser();          // para el template

  /* ⬇️ observable que YA trae locale_name ⬇️ */
  pending$ = this.adminSvc.getPendingWithLocale();

  ngOnInit(): void {
    if (!this.userSnap) { this.auth.initSession().subscribe(); }
  }

  /** Aprueba la reserva */
  approve(res: ReservationWithLocale): void {
    this.adminSvc.setReservationStatus(res.id, 'approved').subscribe(() => {
      alert('Reserva aprobada');
      this.reload();
    });
  }

  /** Rechaza la reserva */
  reject(res: ReservationWithLocale): void {
    this.adminSvc.setReservationStatus(res.id, 'rejected').subscribe(() => {
      alert('Reserva rechazada');
      this.reload();
    });
  }

  /** Recarga la lista de pendientes */
  private reload(): void {
    this.pending$ = this.adminSvc.getPendingWithLocale();
  }

  logout(): void {
    this.auth.logout();
    window.location.href = '/login';
  }
}