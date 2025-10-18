import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ReservationService } from '../../services/reservation.service';
import { LocaleService } from '../../services/locale.service';

// Importaciones de modelos actualizados (asumiendo que los modelos fueron modificados)
import { AvailabilityResponse, TimeRange, ReservationDisplay } from '../../models/availability.model';
import { ReservationCreate } from '../../models/reservation.model';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  // Agregamos DatePipe para su uso en el template
  imports: [CommonModule, FormsModule, DatePipe], 
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
  // Usamos ReservationDisplay[] que incluye status
  reservations: ReservationDisplay[] = []; 

  /* ---------- Lógica de Disponibilidad ---------- */
  selectedLocaleId: string | null = null;
  // Inicializamos la fecha con hoy en formato YYYY-MM-DD para el input[type=date]
  searchDate: string = new Date().toISOString().substring(0, 10);
  availability: AvailabilityResponse | null = null;
  loadingAvailability: boolean = false;
  reservationMessage: string = '';

  // Bloque continuo seleccionado por el usuario (Tipo: TimeRange)
  selectedBlock: TimeRange | null = null;
  motiveInput: string = '';
  // Horas exactas que el usuario selecciona dentro del bloque (para input[type=datetime-local])
  reservationStart: string = '';
  reservationEnd: string = '';

  ngOnInit(): void {
    if (!this.userSnap) {
      this.auth.initSession().subscribe();
    }
    this.loadData();
  }

  loadData(): void {
    this.localeSvc.list().subscribe(data => this.locales = data);
    // Aseguramos que las reservas cargadas tengan el status
    this.reservationSvc.myReservations().subscribe((data: any) => this.reservations = data);
  }

  // Consultar la disponibilidad de un local para la fecha seleccionada
  checkAvailability(localeId: string): void {
    this.selectedLocaleId = localeId;
    this.selectedBlock = null; // Reiniciar selección de bloque
    this.availability = null;
    this.loadingAvailability = true;
    this.reservationMessage = '';

    this.localeSvc.getAvailability(localeId, this.searchDate).subscribe({
      next: (data) => {
        // Casteo explícito a la nueva estructura de AvailabilityResponse
        this.availability = data as unknown as AvailabilityResponse;
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

  // 1. Selecciona el bloque continuo y precarga las horas de inicio/fin
  selectBlock(block: TimeRange): void {
      this.selectedBlock = block;
      this.reservationMessage = '';

      // Inicializar el tiempo de reserva con el inicio del bloque
      this.reservationStart = this.getDateTimeLocalString(block.start_dt);
      
      // Inicializar el tiempo de fin con 1 hora después del inicio (o el final del bloque si es más corto)
      const defaultEnd = new Date(new Date(block.start_dt).getTime() + 60 * 60 * 1000);
      const blockEnd = new Date(block.end_dt);
      
      const initialEnd = (defaultEnd <= blockEnd ? defaultEnd : blockEnd);
      this.reservationEnd = this.getDateTimeLocalString(initialEnd.toISOString());
  }

  // 2. Validación de la reserva (asegura que esté dentro del bloque y que sea válida)
  isReservationValid(): boolean {
      if (!this.selectedBlock || !this.reservationStart || !this.reservationEnd) return false;
      
      const start = new Date(this.reservationStart);
      const end = new Date(this.reservationEnd);
      const minBlock = new Date(this.selectedBlock.start_dt);
      const maxBlock = new Date(this.selectedBlock.end_dt);

      // 1. Fin debe ser posterior a inicio y con duración mínima (ej: 30 minutos)
      if (end <= start || (end.getTime() - start.getTime()) < 30 * 60 * 1000) return false;
      
      // 2. Debe estar dentro del bloque continuo seleccionado
      // Usamos getTime() para comparación precisa
      if (start.getTime() < minBlock.getTime() || end.getTime() > maxBlock.getTime()) return false;
      
      return true;
  }
  
  // 3. Crea la reserva usando las horas personalizadas y motivo
  onReserve(localeId: string): void {
    const motive = this.motiveInput.trim();
    if (!this.isReservationValid()) {
      alert('Error de validación: Las horas seleccionadas no son válidas o no están dentro del bloque continuo seleccionado.');
      return;
    }
    if (!motive) {
      alert('Error: El motivo de la reserva es obligatorio.');
      return;
    }
    
    // Importante: Convertir las horas locales del input a formato ISO (UTC) para el backend
    // Al crear un new Date() con el string datetime-local, el navegador lo interpreta en la zona local, 
    // y toISOString() lo convierte a UTC.
    const startIso = new Date(this.reservationStart).toISOString();
    const endIso = new Date(this.reservationEnd).toISOString();

    const reservationPayload: ReservationCreate = {
      locale_id: localeId,
      start_dt: startIso,
      end_dt: endIso,
      motive: motive
    };
    
    this.reservationMessage = 'Enviando solicitud...';

    this.reservationSvc.create(reservationPayload)
      .subscribe({
        next: () => {
          this.reservationMessage = '¡Reserva solicitada! Se permite solapamiento, por lo que su estado es PENDIENTE de aprobación del administrador.';
          this.loadData(); // recargar listados (incluyendo la nueva reserva PENDIENTE en 'Mis reservas')
          this.checkAvailability(localeId); // Recargar disponibilidad para el local actual
          this.selectedBlock = null; // Limpiar selección
          this.motiveInput = ''; // Limpiar motivo
        },
        error: (err) => {
          const detail = err.error?.detail || 'Error desconocido al solicitar la reserva.';
          this.reservationMessage = `Fallo en la reserva: ${detail}`;
          console.error(err);
        }
      });
  }
  
  // Helper para convertir ISO UTC a string compatible con input[datetime-local]
  // Necesario para mostrar la hora en la zona horaria local del navegador.
  getDateTimeLocalString(isoString: string): string {
    const date = new Date(isoString);
    const y = date.getFullYear();
    const m = (date.getMonth() + 1).toString().padStart(2, '0');
    const d = date.getDate().toString().padStart(2, '0');
    const h = date.getHours().toString().padStart(2, '0');
    const mi = date.getMinutes().toString().padStart(2, '0');
    return `${y}-${m}-${d}T${h}:${mi}`;
  }
    
  logout(): void {
    this.auth.logout();
    window.location.href = '/login';
  }
}
