# backend/app/routers/locales.py

from fastapi import APIRouter, Depends, HTTPException, Query # ⬅️ Añadir Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, date # ⬅️ Necesario para manejo de fechas
from uuid import UUID # ⬅️ Necesario para tipado de IDs

from ..models import Locale, Reservation # ⬅️ Necesitas Reservation
from ..schemas import LocaleOut, AvailabilityResponse, TimeSlot # ⬅️ Nuevos Schemas
from ..enums import ReservationStatus # ⬅️ Necesitas el Enum de estado

from ..database import async_session
router = APIRouter()

# 🛠️ Dependencia para obtener la sesión de DB
async def get_async_session():
    async with async_session() as session:
        yield session

@router.get("/", response_model=list[LocaleOut])
async def list_locales():
    async with async_session() as session:
        res = await session.execute(select(Locale).where(Locale.active == True))
        db_rows = res.scalars().all()

    # ⬇️⬇️  convierte a dict y formatea los time ⬇️⬇️
    return [
        {
            **row.__dict__,
            "open_time": row.open_time.strftime("%H:%M"),
            "close_time": row.close_time.strftime("%H:%M"),
        }
        for row in db_rows
    ]

@router.get("/{locale_id}", response_model=LocaleOut)
async def get_locale(locale_id: str):
	async with async_session() as session:
		locale = await session.get(Locale, locale_id)
		if not locale:
			raise HTTPException(status_code=404, detail="Local no encontrado")
		return locale

@router.get("/{locale_id}/availability", response_model=AvailabilityResponse)
async def get_locale_availability(
    locale_id: UUID,
    # El usuario puede especificar una fecha (YYYY-MM-DD)
    search_date: date = Query(default=date.today(), description="Fecha a consultar (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_async_session) # Usar la dependencia local
):
    # 1. Buscar el Local y sus horas de operación
    locale_res = await session.execute(
        select(Locale).where(Locale.id == locale_id, Locale.active == True)
    )
    locale = locale_res.scalar_one_or_none()
    
    if not locale:
        raise HTTPException(status_code=404, detail="Local no encontrado o inactivo")

    # 2. Convertir horas de operación (str) a objetos time
    try:
        # Asumiendo que open_time y close_time en el modelo Locale
        # son guardados como strings que representan "HH:MM"
        open_time = datetime.strptime(locale.open_time, "%H:%M").time()
        close_time = datetime.strptime(locale.close_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=500, detail="Error de configuración del horario del local")
    
    # 3. Definir el rango exacto del día a buscar
    start_of_day = datetime.combine(search_date, open_time)
    end_of_day = datetime.combine(search_date, close_time)

    # 4. Buscar Reservas Confirmadas y Pendientes (las que bloquean el local)
    reservations_res = await session.execute(
        select(Reservation)
        .where(
            Reservation.locale_id == locale_id,
            # Se superpone con el día de búsqueda
            Reservation.start_dt < end_of_day,
            Reservation.end_dt > start_of_day,
            # Solo reservas aprobadas o pendientes bloquean la disponibilidad
            Reservation.status.in_([ReservationStatus.approved, ReservationStatus.pending])
        )
        .order_by(Reservation.start_dt)
    )
    reservations = reservations_res.scalars().all()
    
    # 5. Procesar Reservas y Calcular Slots Ocupados
    occupied_slots = []
    
    for res in reservations:
        # Asegurarse de que los límites del slot estén dentro del horario de apertura/cierre
        start = max(res.start_dt, start_of_day)
        end = min(res.end_dt, end_of_day)
        
        if start < end:
            occupied_slots.append(TimeSlot(start_dt=start, end_dt=end))
    
    # 6. Calcular Slots Disponibles (El Inverso de los Ocupados)
    available_slots = []
    current_time = start_of_day

    # Iterar sobre los slots ocupados para encontrar los huecos
    for slot in occupied_slots:
        # Si el tiempo actual es menor al inicio del slot, hay un hueco libre
        if current_time < slot.start_dt:
            available_slots.append(TimeSlot(start_dt=current_time, end_dt=slot.start_dt))
        
        # Mover el puntero de tiempo al final del slot ocupado (saltando cualquier solapamiento)
        current_time = max(current_time, slot.end_dt)
        
    # Agregar el último hueco libre (desde el último slot ocupado hasta el cierre)
    if current_time < end_of_day:
        available_slots.append(TimeSlot(start_dt=current_time, end_dt=end_of_day))

    # 7. Devolver la respuesta estructurada
    return AvailabilityResponse(
        occupied_slots=occupied_slots,
        available_slots=available_slots
    )