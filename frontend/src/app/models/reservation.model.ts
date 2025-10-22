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

export interface LocaleListItem {
    id: string;
    name: string;
    description: string;
    capacity: number;
    imagen_url: string; // Asumimos que esta URL existe para la imagen del local
}

export interface ReservationFull {
  id: string;
  start_dt: string;
  end_dt: string;
  status: string;
  motive: string;
  userName: string;
  userEmail: string;
  locale: {
    id: string;
    name: string;
    imagen_url: string;
  };
}