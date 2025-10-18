import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Necesario para [(ngModel)]
import { AuthService } from '../../services/auth.service';
import { ReservationService } from '../../services/reservation.service';
import { LocaleService } from '../../services/locale.service';
// ⚠️ Rutas corregidas asumiendo /app/models/         
//import { AvailabilityResponse, TimeSlot } from 'src/app/models/availability.model';                                              
import { AvailabilityResponse, TimeSlot } from '../../models/availability.model';
import { ReservationCreate } from '../../models/reservation.model';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {

  private auth = inject(AuthService);
  private reservationSvc = inject(ReservationService);
  private localeSvc = inject(LocaleService);

  /* ---------- usuario ---------- */
  user$ = this.auth.getUser();
  private get userSnap() { return (this.auth as any)['user$'].value; }

  /* ---------- datos base ---------- */
  locales: any[] = [];
  reservations: any[] = [];

  /* ---------- Lógica de Disponibilidad ---------- */
  selectedLocaleId: string | null = null;
  // Inicializamos la fecha con hoy en formato YYYY-MM-DD para el input[type=date]
  searchDate: string = new Date().toISOString().substring(0, 10);
  availability: AvailabilityResponse | null = null;
  loadingAvailability: boolean = false;

  // Slot seleccionado por el usuario y motivo
  selectedSlot: TimeSlot | null = null;
  motiveInput: string = '';

  ngOnInit(): void {
    if (!this.userSnap) {
      this.auth.initSession().subscribe();
    }
    this.loadData();
  }

  loadData(): void {
    this.localeSvc.list().subscribe(data => this.locales = data);
    this.reservationSvc.myReservations().subscribe(data => this.reservations = data);
  }

  // Consultar la disponibilidad de un local para la fecha seleccionada
  checkAvailability(localeId: string): void {
    this.selectedLocaleId = localeId;
    this.selectedSlot = null;
    this.availability = null;
    this.loadingAvailability = true;

    this.localeSvc.getAvailability(localeId, this.searchDate).subscribe({
      next: (data) => {
        this.availability = {
          occupied_slots: (data as any).occupied_slots || [],
          available_slots: (data as any).available_slots || []
        };
        this.loadingAvailability = false;
      },
      error: (err) => {
        alert('Error al obtener disponibilidad. Revise la consola.');
        console.error(err);
        this.loadingAvailability = false;
        this.availability = null;
      }
    });
  }

  // Crea la reserva usando el slot y motivo seleccionado
  onReserve(localeId: string): void {
    if (!this.selectedSlot) {
      alert('Error: Debe seleccionar un horario disponible.');
      return;
    }

    const motive = this.motiveInput.trim();
    if (!motive) {
      alert('Error: El motivo de la reserva es obligatorio.');
      return;
    }

    // Usar el modelo ReservationCreate
    const reservationPayload: ReservationCreate = {
      locale_id: localeId,
      start_dt: this.selectedSlot.start_dt,
      end_dt: this.selectedSlot.end_dt,
      motive: motive
    };

    this.reservationSvc.create(reservationPayload)
      .subscribe({
        next: () => {
          alert('Reserva solicitada y enviada a revisión (PENDIENTE).');
          this.loadData(); // recargar listados
          this.selectedLocaleId = null; // Cerrar el panel
          this.motiveInput = ''; // Limpiar motivo
        },
        error: (err) => {
          const detail = err.error?.detail || 'Error desconocido';
          alert(`Fallo en la reserva: ${detail}`);
        }
      });
  }
  
  logout(): void {
    this.auth.logout();
    window.location.href = '/login';
  }
}
