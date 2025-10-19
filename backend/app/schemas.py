#backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from .enums import ReservationStatus   # si quieres restringir valores
from typing import Optional

# ---------- AUTH ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- LOCALES ----------
class LocaleOut(BaseModel):
    id: UUID
    name: str
    description: str
    capacity: int
    location: str
    open_time: str
    close_time: str
    active: bool

    class Config:
        from_attributes = True   # V2 (ex-orm_mode)

# ---------- RESERVAS ----------
class ReservationCreate(BaseModel):
    locale_id: UUID
    start_dt: datetime
    end_dt: datetime
    motive: str

class ReservationStatusUpdate(BaseModel):
    """Modelo para recibir el cuerpo JSON en la ruta PATCH de status."""
    # Esto espera el JSON: {"status": "approved"}
    status: ReservationStatus

class ReservationOut(BaseModel):
    id: UUID
    locale_id: UUID
    user_id: UUID
    start_dt: datetime
    end_dt: datetime
    motive: str
    status: str          # o  status: ReservationStatus
    priority: int

    class Config:
        from_attributes = True   # V2

# ➜➜➜  NUEVO: reserva con nombre del local
class ReservationWithLocaleOut(BaseModel):
    id: UUID
    locale_id: UUID
    locale_name: str          # ← campo extra
    user_id: UUID
    start_dt: datetime
    end_dt: datetime
    motive: str
    status: str
    priority: int

    class Config:
        from_attributes = True

# Esquema para representar un periodo de tiempo (ocupado o disponible)
class TimeSlot(BaseModel):
    start_dt: datetime
    end_dt: datetime

# Este esquema refleja la respuesta enriquecida que crea tu router
class ReservationDisplay(TimeSlot):
    # Campos heredados de TimeSlot: start_dt, end_dt
    
    # Campos adicionales requeridos por el frontend y generados por el router
    id: str # O UUID, dependiendo de cómo lo serialices en el router
    status: str
    user: str  # Email del usuario (obtenido del JOIN)
    status_color: str # 'green', 'yellow', 'gray'

    # Campos opcionales
    locale_name: Optional[str] = None
    display_text: Optional[str] = None

# Esquema de Respuesta para la Disponibilidad
class AvailabilityResponse(BaseModel):
    # Los horarios ocupados (reservas confirmadas o pendientes)
    occupied_slots: list[TimeSlot]
    # Los horarios que el local está abierto pero no reservado
    available_slots: list[TimeSlot]

