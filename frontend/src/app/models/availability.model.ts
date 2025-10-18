export interface TimeSlot {
  start_dt: string;
  end_dt: string;
}

export interface AvailabilityResponse {
  occupied_slots: TimeSlot[];
  available_slots: TimeSlot[];
}