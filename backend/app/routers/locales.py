from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, date
from uuid import UUID

# Importaciones de modelos y esquemas
from ..models import Locale, Reservation
# NOTA: Asumo que AvailabilityResponse en ..schemas ahora acepta 'available_blocks' 
# en lugar de 'available_slots' para manejar esta nueva lógica.
from ..schemas import LocaleOut, AvailabilityResponse, TimeSlot, ReservationCreate, ReservationOut
from ..enums import ReservationStatus

from ..database import async_session
router = APIRouter()

# 🛠️ CONSTANTE: Duración de cada slot que el usuario puede reservar
RESERVATION_SLOT_DURATION = timedelta(hours=1) 
# ⚠️ IMPORTANTE: Este ID es un placeholder y debe ser reemplazado por la autenticación del usuario.
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001") 

# Dependencia para obtener la sesión de DB
async def get_async_session():
    async with async_session() as session:
        yield session

@router.get("/", response_model=list[LocaleOut])
async def list_locales(session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(Locale).where(Locale.active == True))
    db_rows = res.scalars().all()

    return [
        {
            **row.__dict__,
            "open_time": row.open_time.strftime("%H:%M"),
            "close_time": row.close_time.strftime("%H:%M"),
        }
        for row in db_rows
    ]

@router.get("/{locale_id}", response_model=LocaleOut)
async def get_locale(locale_id: UUID, session: AsyncSession = Depends(get_async_session)):
    locale = await session.get(Locale, locale_id)
    if not locale:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    return locale

@router.get("/{locale_id}/availability", response_model=AvailabilityResponse)
async def get_locale_availability(
    locale_id: UUID,
    search_date: date = Query(default=date.today(), description="Fecha a consultar (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Buscar el Local y sus horas de operación
    locale = await session.get(Locale, locale_id)
    
    if not locale or not locale.active:
        raise HTTPException(status_code=404, detail="Local no encontrado o inactivo")

    # 2. Obtener las horas de operación
    if isinstance(locale.open_time, time):
        open_t = locale.open_time
        close_t = locale.close_time
    else:
        try:
            open_t = datetime.strptime(locale.open_time, "%H:%M").time()
            close_t = datetime.strptime(locale.close_time, "%H:%M").time()
        except (ValueError, TypeError):
            raise HTTPException(status_code=500, detail="Horario del local mal configurado (no es 'HH:MM').")
    
    # 3. Definir el rango exacto del día a buscar
    start_of_day = datetime.combine(search_date, open_t)
    end_of_day = datetime.combine(search_date, close_t)
    
    if end_of_day <= start_of_day:
        end_of_day += timedelta(days=1)

    # 4. Buscar Reservas Confirmadas y Pendientes (las que bloquean el local)
    reservations_res = await session.execute(
        select(Reservation)
        .where(
            Reservation.locale_id == locale_id,
            Reservation.start_dt < end_of_day,
            Reservation.end_dt > start_of_day,
            Reservation.status.in_([ReservationStatus.approved, ReservationStatus.pending])
        )
        .order_by(Reservation.start_dt)
    )
    reservations = reservations_res.scalars().all()
    
    # 5. Procesar Reservas y Calcular Slots Ocupados
    occupied_slots = []
    for res in reservations:
        start = max(res.start_dt, start_of_day)
        end = min(res.end_dt, end_of_day)
        
        if start < end:
            occupied_slots.append(TimeSlot(start_dt=start, end_dt=end))
    
    # 6. 🛠️ CÁLCULO DE BLOQUES DISPONIBLES CONTINUOS (El Hueco entre Reservas)
    available_blocks = []
    current_time = start_of_day

    for slot in occupied_slots:
        # Si el tiempo actual es menor al inicio del slot, hay un hueco libre
        if current_time < slot.start_dt:
            # Se encontró un bloque continuo (e.g., 7:00 AM - 10:00 AM)
            available_blocks.append(TimeSlot(start_dt=current_time, end_dt=slot.start_dt))
        
        # Mover el puntero al final del slot ocupado
        current_time = max(current_time, slot.end_dt)
        
    # Agregar el último hueco libre (desde el último slot ocupado hasta el cierre)
    if current_time < end_of_day:
        available_blocks.append(TimeSlot(start_dt=current_time, end_dt=end_of_day))

    # 7. Devolver la respuesta estructurada
    # NOTA: El frontend debe manejar que 'occupied_slots' ya no significa 'inaccesible'
    return AvailabilityResponse(
        occupied_slots=occupied_slots,
        available_slots=available_blocks # Usamos 'available_slots' para compatibilidad con la interfaz
    )

