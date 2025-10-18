from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, date
from uuid import UUID

from ..models import Locale, Reservation
from ..schemas import LocaleOut, AvailabilityResponse, TimeSlot
from ..enums import ReservationStatus

from ..database import async_session
router = APIRouter()

# 🛠️ CONSTANTE: Duración de cada slot que el usuario puede reservar
RESERVATION_SLOT_DURATION = timedelta(hours=1) 

# Dependencia para obtener la sesión de DB
async def get_async_session():
    async with async_session() as session:
        yield session

@router.get("/", response_model=list[LocaleOut])
async def list_locales(session: AsyncSession = Depends(get_async_session)): # Añadir sesión aquí
    res = await session.execute(select(Locale).where(Locale.active == True))
    db_rows = res.scalars().all()

    # ⬇️⬇️  convierte a dict y formatea los time ⬇️⬇️
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
    # FastAPI convierte automáticamente el string 'YYYY-MM-DD' a datetime.date
    search_date: date = Query(default=date.today(), description="Fecha a consultar (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Buscar el Local y sus horas de operación
    locale = await session.get(Locale, locale_id)
    
    if not locale or not locale.active:
        raise HTTPException(status_code=404, detail="Local no encontrado o inactivo")

    # 2. Obtener las horas de operación (CORRECCIÓN DE TIPO)
    # Si Locale.open_time es un objeto time, lo usamos. Si es string 'HH:MM', lo convertimos.
    if isinstance(locale.open_time, time):
        open_t = locale.open_time
        close_t = locale.close_time
    else:
        # Asumimos que es string si no es time, y forzamos la conversión (para evitar el error original)
        try:
            open_t = datetime.strptime(locale.open_time, "%H:%M").time()
            close_t = datetime.strptime(locale.close_time, "%H:%M").time()
        except (ValueError, TypeError):
            raise HTTPException(status_code=500, detail="Horario del local mal configurado (no es 'HH:MM').")
    
    # 3. Definir el rango exacto del día a buscar (datetimes completos)
    start_of_day = datetime.combine(search_date, open_t)
    end_of_day = datetime.combine(search_date, close_t)
    
    # Manejar caso de cierre el día siguiente (ej. 22:00 a 02:00)
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
    # 💡 CORRECCIÓN: Almacenar objetos datetime en TimeSlot (asumiendo que TimeSlot usa datetime.datetime)
    # y dejar que Pydantic maneje la serialización ISO al final.
    occupied_slots = []
    for res in reservations:
        start = max(res.start_dt, start_of_day)
        end = min(res.end_dt, end_of_day)
        
        if start < end:
            # Quitamos .isoformat() para evitar el TypeError
            occupied_slots.append(TimeSlot(start_dt=start, end_dt=end))
    
    # 6. 🛠️ CÁLCULO DE SLOTS DISPONIBLES DISCRETOS (Arreglo Lógico)
    all_slots = []
    current_slot_start = start_of_day
    
    # Generar todos los slots posibles del día (ej. 10:00-11:00, 11:00-12:00, etc.)
    while current_slot_start + RESERVATION_SLOT_DURATION <= end_of_day:
        slot_end = current_slot_start + RESERVATION_SLOT_DURATION
        all_slots.append({'start': current_slot_start, 'end': slot_end})
        current_slot_start = slot_end

    # Filtrar los slots disponibles
    available_slots = []
    
    for slot in all_slots:
        is_available = True
        
        # Verificar si el slot actual se superpone con algún slot ocupado
        for occupied in occupied_slots:
            # 💡 CORRECCIÓN: Acceder directamente a los objetos datetime, no re-parsearlos.
            occupied_start = occupied.start_dt
            occupied_end = occupied.end_dt
            
            # Condición de solapamiento: (A_inicio < B_fin) AND (A_fin > B_inicio)
            if slot['start'] < occupied_end and slot['end'] > occupied_start:
                is_available = False
                break
        
        if is_available:
            # 💡 CORRECCIÓN: Almacenar objetos datetime.
            available_slots.append(TimeSlot(
                start_dt=slot['start'],
                end_dt=slot['end']
            ))

    # 7. Devolver la respuesta estructurada
    return AvailabilityResponse(
        occupied_slots=occupied_slots,
        available_slots=available_slots
    )
