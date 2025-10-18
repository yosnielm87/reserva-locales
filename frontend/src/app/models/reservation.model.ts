// Este modelo se usa para enviar datos al POST /reservations
export interface ReservationCreate {
    locale_id: string; // UUID del local
    start_dt: string;  // Fecha y hora de inicio (ISO string)
    end_dt: string;    // Fecha y hora de fin (ISO string)
    motive: string;
}

// Puedes añadir la respuesta de la API aquí también
export interface ReservationOut {
    id: string;
    locale_id: string;
    user_id: string;
    start_dt: string;
    end_dt: string;
    motive: string;
    status: string; // 'pending', 'approved', 'rejected'
}
