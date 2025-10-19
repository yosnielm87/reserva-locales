import { Component, OnInit, Input } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LocaleService } from '../../services/locale.service';
// Asumo que estos modelos están definidos correctamente:
import { AvailabilityResponse, TimeRange, ReservationDisplay } from '../../models/availability.model';

// Definimos el tipo enriquecido para la visualización en el calendario
type CalendarSlot = (ReservationDisplay | TimeRange) & { type: 'available' | 'occupied' };


@Component({
  selector: 'app-availability-calendar',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe], 
  templateUrl: './availability-calendar.component.html',
  styleUrls: ['./availability-calendar.component.css']
})
export class AvailabilityCalendarComponent implements OnInit {

  @Input() localeId!: string;
  selectedDate: string = new Date().toISOString().substring(0, 10);
  availability!: AvailabilityResponse;
  loading = false;

  constructor(private localeService: LocaleService) { }

  ngOnInit(): void {
    if (this.localeId) this.fetchAvailability();
  }

  onDateChange(): void {
    this.fetchAvailability();
  }

  fetchAvailability(): void {
    if (!this.localeId || !this.selectedDate) return;

    this.loading = true;
    this.localeService.getAvailability(this.localeId, this.selectedDate)
      .subscribe({
        next: (body: any) => {
          this.availability = {
            occupied_slots: (body.occupied_slots as ReservationDisplay[]) || [],
            available_slots: (body.available_slots as TimeRange[]) || []
          };
          this.loading = false;
        },
        error: (err) => {
          console.error('Error al cargar disponibilidad:', err);
          this.loading = false;
        }
      });
  }

  get allSlots(): CalendarSlot[] {
    if (!this.availability) return [];

    const available = this.availability.available_slots
      .map((slot: TimeRange) => ({ ...slot, type: 'available' as const }));
    
    const occupied = this.availability.occupied_slots
      .map((slot: ReservationDisplay) => ({ ...slot, type: 'occupied' as const }));

    return [...available, ...occupied].sort(
      (a, b) => new Date(a.start_dt).getTime() - new Date(b.start_dt).getTime()
    );
  }
    
  // 🛠️ NUEVO HELPER para obtener el color (Amarillo/Verde)
  getSlotColor(slot: CalendarSlot): string {
    if (slot.type === 'occupied') {
      const occupiedSlot = slot as ReservationDisplay;
      return occupiedSlot.status_color === 'green' ? 'var(--color-green-indicator)' : 'var(--color-yellow-indicator)';
    }
    return 'transparent'; // Para slots disponibles
  }

  // 🛠️ NUEVO HELPER para obtener la información detallada (Estado + Usuario)
  getSlotDetails(slot: CalendarSlot): string {
    if (slot.type === 'occupied') {
      const occupiedSlot = slot as ReservationDisplay;
      const statusText = occupiedSlot.status.toUpperCase();
      return `${statusText} (${occupiedSlot.user})`;
    }
    return 'LIBRE';
  }
    
  // 🛠️ FUNCIÓN FALTANTE QUE CAUSA EL ERROR TS2339
  getSlotBgClass(slot: CalendarSlot): string {
      if (slot.type === 'occupied') {
          const occupiedSlot = slot as ReservationDisplay;
          // Devuelve la clase SCSS (status-green o status-yellow) basada en el backend
          return occupiedSlot.status_color === 'green' ? 'status-green' : 'status-yellow';
      }
      // Para slots disponibles, devolvemos 'slot-available' (o puedes devolver '')
      return 'slot-available';
  }
}