// src/app/components/availability-calendar/availability-calendar.component.ts

import { Component, OnInit, Input } from '@angular/core';
import { LocaleService } from '../../services/locale.service';
import { AvailabilityResponse, TimeSlot } from '../../models/reservation.model';


@Component({
  selector: 'app-availability-calendar',
  templateUrl: './availability-calendar.component.html',
  styleUrls: ['./availability-calendar.component.css']
})
export class AvailabilityCalendarComponent implements OnInit {

  @Input() localeId!: string; // El ID del local a consultar
  selectedDate: string = new Date().toISOString().substring(0, 10); // Hoy en 'YYYY-MM-DD'
  availability!: AvailabilityResponse;
  loading: boolean = false;

  constructor(private adminService: LocaleService) { }

  ngOnInit(): void {
    if (this.localeId) {
      this.fetchAvailability();
    }
  }

  fetchAvailability(): void {
    if (!this.localeId || !this.selectedDate) return;
    
    this.loading = true;
    this.adminService.getAvailability(this.localeId, this.selectedDate)
      .subscribe({
        next: (response) => {
          // Asegura que la respuesta tenga las propiedades requeridas por AvailabilityResponse
          this.availability = {
            ...response as any,
            available_slots: (response as any)?.available_slots ?? [],
            occupied_slots: (response as any)?.occupied_slots ?? []
          };
          this.loading = false;
        },
        error: (err) => {
          console.error('Error al cargar disponibilidad:', err);
          this.loading = false;
          // Manejar errores (ej. local no encontrado)
        }
      });
  }

  // Helper para facilitar la visualización en el template
  get allSlots(): (TimeSlot & { type: 'available' | 'occupied' })[] {
    if (!this.availability) return [];

    const available = this.availability.available_slots.map(slot => ({...slot, type: 'available' as const}));
    const occupied = this.availability.occupied_slots.map(slot => ({...slot, type: 'occupied' as const}));

    // Combina y ordena todos los slots por hora de inicio
    return [...available, ...occupied].sort((a, b) => 
      new Date(a.start_dt).getTime() - new Date(b.start_dt).getTime()
    );
  }
}