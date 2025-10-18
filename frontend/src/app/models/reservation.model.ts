// Modelo para enviar una nueva solicitud de reserva al POST /reservations
export interface ReservationCreate {
    locale_id: string; // UUID del local
    start_dt: string; // Fecha y hora de inicio exacta (ISO string)
    end_dt: string; // Fecha y hora de fin exacta (ISO string)
    motive: string;    // Motivo de la reserva (obligatorio)
}

// Modelo de la respuesta de la API al crear o listar reservas
export interface ReservationOut {
    id: string;
    locale_id: string;
    user_id: string;
    start_dt: string;
    end_dt: string;
    motive: string;
    status: string; // 'pending', 'approved', 'rejected', etc.
}