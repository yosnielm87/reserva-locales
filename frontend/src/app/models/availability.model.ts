// Usamos TimeRange para referirnos a un bloque continuo de tiempo (disponible u ocupado)
export interface TimeRange {
  start_dt: string;
  end_dt: string;
}

// Extensión de TimeRange para las reservas que ya existen (ocupadas)
// Incluye el estado para la lógica de solapamiento (pendiente, aprobado, etc.)
export interface ReservationDisplay extends TimeRange {
  id: string;
  status: 'pending' | 'approved' | 'rejected' | string;
  // Puedes añadir locale_name si se recibe al listar las propias reservas
  locale_name?: string;
}

export interface AvailabilityResponse {
  // Los slots ocupados ahora incluyen el ID y el estado de la reserva
  occupied_slots: ReservationDisplay[];
  // Los slots disponibles siguen siendo TimeRange (bloques continuos)
  available_slots: TimeRange[];
}