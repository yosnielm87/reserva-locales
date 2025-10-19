import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ReservationService } from '../../services/reservation.service';
import { LocaleService } from '../../services/locale.service';

// Interfaces (ajustá la ruta si las tenés en otro archivo)
export interface TimeRange {
  start_dt: string;
  end_dt: string;
}

export interface AvailabilityResponse {
  available_slots: TimeRange[];
  occupied_slots: any[];
}

export interface ReservationCreate {
  locale_id: string;
  start_dt: string;
  end_dt: string;
  motive: string;
}

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe],
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {

  /* ---------- Servicios ---------- */
  private auth = inject(AuthService);
  private reservationSvc = inject(ReservationService);
  private localeSvc = inject(LocaleService);

  /* ---------- Usuario ---------- */
  user$ = this.auth.getUser();
  private get userSnap() { return (this.auth as any)['user$']?.value; }

  /* ---------- Tabs ---------- */
  activeTab: 'new' | 'upcoming' | 'history' = 'new';

  /* ---------- Datos base ---------- */
  locales: any[] = [];
  upcoming$ = this.reservationSvc.upcoming(this.userSnap?.id ?? '');
  history$ = this.reservationSvc.history(this.userSnap?.id ?? '');

  /* ---------- Nueva Reserva ---------- */
  searchDate: string = new Date().toISOString().substring(0, 10);
  selectedLocaleId: string | null = null;
  availability: AvailabilityResponse | null = null;
  loadingAvailability = false;
  reservationMessage = '';
  selectedBlock: TimeRange | null = null;
  motiveInput = '';
  reservationStart = '';
  reservationEnd = '';

  ngOnInit(): void {
    if (!this.userSnap) this.auth.initSession().subscribe();
    this.loadLocales();
  }

  loadLocales(): void {
    this.localeSvc.list().subscribe(data => this.locales = data);
  }

  /* ---------- Lógica de Disponibilidad ---------- */
  checkAvailability(localeId: string): void {
    this.selectedLocaleId = localeId;
    this.selectedBlock = null;
    this.availability = null;
    this.loadingAvailability = true;
    this.reservationMessage = '';

    this.localeSvc.getAvailability(localeId, this.searchDate).subscribe({
      next: (data) => {
        this.availability = data as unknown as AvailabilityResponse;
        this.loadingAvailability = false;
      },
      error: (err) => {
        console.error(err);
        this.loadingAvailability = false;
        this.availability = null;
      }
    });
  }

  selectBlock(block: TimeRange): void {
    this.selectedBlock = block;
    this.reservationMessage = '';
    // Precarga horas por defecto
    this.reservationStart = this.getDateTimeLocalString(block.start_dt);
    const defaultEnd = new Date(new Date(block.start_dt).getTime() + 60 * 60 * 1000);
    const blockEnd = new Date(block.end_dt);
    const initialEnd = defaultEnd <= blockEnd ? defaultEnd : blockEnd;
    this.reservationEnd = this.getDateTimeLocalString(initialEnd.toISOString());
  }

  isReservationValid(): boolean {
    if (!this.selectedBlock || !this.reservationStart || !this.reservationEnd) return false;
    const start = new Date(this.reservationStart);
    const end = new Date(this.reservationEnd);
    const minBlock = new Date(this.selectedBlock.start_dt);
    const maxBlock = new Date(this.selectedBlock.end_dt);
    return (
      end > start &&
      (end.getTime() - start.getTime()) >= 30 * 60 * 1000 &&
      start >= minBlock &&
      end <= maxBlock
    );
  }

  onReserve(localeId: string): void {
    if (!this.isReservationValid() || !this.motiveInput.trim()) {
      alert('Completa todos los campos y asegúrate de que el rango sea válido.');
      return;
    }
    const payload: ReservationCreate = {
      locale_id: localeId,
      start_dt: new Date(this.reservationStart).toISOString(),
      end_dt: new Date(this.reservationEnd).toISOString(),
      motive: this.motiveInput.trim()
    };

    this.reservationMessage = 'Enviando solicitud...';
    this.reservationSvc.create(payload).subscribe({
      next: () => {
        this.reservationMessage = '¡Reserva solicitada! Estado: PENDIENTE.';
        this.motiveInput = '';
        this.selectedBlock = null;
        this.loadLocales();          // recarga lista
        this.upcoming$ = this.reservationSvc.upcoming(this.userSnap?.id ?? '');
      },
      error: (err) => {
        this.reservationMessage = `Fallo: ${err.error?.detail || 'Error desconocido'}`;
      }
    });
  }

  cancel(reservationId: string): void {
    this.reservationSvc.cancel(reservationId).subscribe(() => {
      this.upcoming$ = this.reservationSvc.upcoming(this.userSnap?.id ?? '');
    });
  }

  /* ---------- Helper ---------- */
  getDateTimeLocalString(iso: string): string {
    const d = new Date(iso);
    return `${d.getFullYear()}-${('0' + (d.getMonth() + 1)).slice(-2)}-${('0' + d.getDate()).slice(-2)}T${('0' + d.getHours()).slice(-2)}:${('0' + d.getMinutes()).slice(-2)}`;
  }

  getLocaleName(id: string): string {
    return this.locales.find(l => l.id === id)?.name || 'Local desconocido';
  }

  getLocaleImage(localeId: string): string {
    const loc = this.locales.find(l => l.id === localeId);
    return loc?.imagen_url || '/assets/img/no-image.jpg';
  }

}