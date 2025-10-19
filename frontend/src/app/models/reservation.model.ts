// Para crear
export interface ReservationCreate {
  locale_id: string;
  start_dt: string;
  end_dt: string;
  motive: string;
}

// Para leer / listar
export interface ReservationOut {
  id: string;
  locale_id: string;
  user_id: string;
  start_dt: string;
  end_dt: string;
  motive: string;
  status: string; // 'pending' | 'approved' | 'rejected', etc.
}

// Para listar con datos del local
export interface ReservationWithLocale extends ReservationOut {
  locale_name: string;
}