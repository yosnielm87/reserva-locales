export interface LocaleCreate {
  name: string;
  description: string;
  capacity: number;
  location: string;
  open_time: string;
  close_time: string;
  imagen?: File;
}

export interface LocaleOut {
  id: string;
  name: string;
  description: string;
  capacity: number;
  location: string;
  open_time: string;
  close_time: string;
  imagen_url: string;
}