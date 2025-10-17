#backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from .enums import ReservationStatus   # si quieres restringir valores

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

