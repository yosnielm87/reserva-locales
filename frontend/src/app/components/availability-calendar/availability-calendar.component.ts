// src/app/components/availability-calendar/availability-calendar.component.ts

import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { LocaleService } from '../../services/locale.service';
import { AvailabilityResponse, TimeSlot } from '../../models/availability.model';

@Component({
  selector: 'app-availability-calendar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './availability-calendar.component.html',
  styleUrls: ['./availability-calendar.component.scss']
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

  fetchAvailability(): void {
    if (!this.localeId || !this.selectedDate) return;

    this.loading = true;
    this.localeService.getAvailability(this.localeId, this.selectedDate)
      .subscribe({
        next: (body: any) => {
          this.availability = {
            occupied_slots: (body.occupied_slots as TimeSlot[]) || [],
            available_slots: (body.available_slots as TimeSlot[]) || []
          };
          this.loading = false;
        },
        error: (err) => {
          console.error('Error al cargar disponibilidad:', err);
          this.loading = false;
        }
      });
  }


  /* Helper tipado: devuelve slots enriquecidos y ordenados por hora */
  get allSlots(): (TimeSlot & { type: 'available' | 'occupied' })[] {
    if (!this.availability) return [];

    const available = this.availability.available_slots
      .map((slot: TimeSlot) => ({ ...slot, type: 'available' as const }));
    const occupied = this.availability.occupied_slots
      .map((slot: TimeSlot) => ({ ...slot, type: 'occupied' as const }));

    return [...available, ...occupied].sort(
      (a, b) => new Date(a.start_dt).getTime() - new Date(b.start_dt).getTime()
    );
  }
}