from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta, date
from uuid import UUID

# Importaciones de modelos y esquemas
from ..models import Locale, Reservation, User
from ..schemas import LocaleOut, AvailabilityResponse, TimeSlot, ReservationCreate, ReservationOut, ReservationDisplay
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
            # Asumo que los campos open_time y close_time son objetos time o string que necesitan formato
            "open_time": row.open_time.strftime("%H:%M") if isinstance(row.open_time, time) else str(row.open_time),
            "close_time": row.close_time.strftime("%H:%M") if isinstance(row.close_time, time) else str(row.close_time),
            "imagen_url": f"/assets/locales/{row.imagen}"
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
            # Intentamos parsear HH:MM si es un string (asumiendo que en DB es string o time)
            open_t = datetime.strptime(str(locale.open_time), "%H:%M").time()
            close_t = datetime.strptime(str(locale.close_time), "%H:%M").time()
        except (ValueError, TypeError):
            raise HTTPException(status_code=500, detail="Horario del local mal configurado (no es 'HH:MM').")
    
    # 3. Definir el rango exacto del día a buscar
    start_of_day = datetime.combine(search_date, open_t).replace(tzinfo=None)
    end_of_day = datetime.combine(search_date, close_t).replace(tzinfo=None)
    
    if end_of_day <= start_of_day:
        end_of_day += timedelta(days=1)

    # 4. BUSCAR RESERVAS CON DETALLE DE USUARIO Y ESTADO
    
    # 🛠️ IMPORTANTE: Incluimos Reservation.id para satisfacer la validación de Pydantic
    stmt = (
        select(
            Reservation.id, # ⬅️ CAMBIO CLAVE: Solución al error "id is missing"
            Reservation.start_dt,
            Reservation.end_dt,
            Reservation.status,
            User.email.label("user_email") # Obtenemos el email
        )
        .join(User, Reservation.user_id == User.id) 
        .where(
            Reservation.locale_id == locale_id,
            Reservation.start_dt < end_of_day,
            Reservation.end_dt > start_of_day,
            Reservation.status.in_([ReservationStatus.approved, ReservationStatus.pending])
        )
        .order_by(Reservation.start_dt)
    )

    occupied_results = await session.execute(stmt)
    
    # 5. Procesar Reservas y Crear Slots Ocupados ENRIQUECIDOS
    
    occupied_slots_raw = [] 
    occupied_slots_enriched = [] 
    
    for row in occupied_results:
        # Extraemos el ID
        res_id = row.id
        res_start_dt = row.start_dt.replace(tzinfo=None)
        res_end_dt = row.end_dt.replace(tzinfo=None)
        res_status = row.status
        user_email = row.user_email
        
        # Recortamos el slot al rango de búsqueda
        start = max(res_start_dt, start_of_day)
        end = min(res_end_dt, end_of_day)
        
        if start < end:
            # Lógica de Color para el frontend
            if res_status == ReservationStatus.approved:
                color_indicator = "green"
            elif res_status == ReservationStatus.pending:
                color_indicator = "yellow"
            else:
                color_indicator = "gray"
            
            # 1. Slot para el CÁLCULO de huecos libres (TimeSlot básico)
            occupied_slots_raw.append(TimeSlot(start_dt=start, end_dt=end))
            
            # 2. Slot para la RESPUESTA ENRIQUECIDA (ReservationDisplay)
            occupied_slots_enriched.append(
                ReservationDisplay(
                    id=str(res_id), # ⬅️ Solución a la ValidationError (id obligatorio)
                    start_dt=start, 
                    end_dt=end,
                    status=res_status.value, 
                    user=user_email,
                    status_color=color_indicator,
                    display_text=f"{res_status.value.upper()} ({user_email})"
                )
            )
    
    # 6. CÁLCULO DE BLOQUES DISPONIBLES CONTINUOS
    available_blocks = []
    current_time = start_of_day

    for slot in occupied_slots_raw:
        if current_time < slot.start_dt:
            available_blocks.append(TimeSlot(start_dt=current_time, end_dt=slot.start_dt))
        current_time = max(current_time, slot.end_dt)
        
    if current_time < end_of_day:
        available_blocks.append(TimeSlot(start_dt=current_time, end_dt=end_of_day))

    # 7. Devolver la respuesta estructurada
    return AvailabilityResponse(
        occupied_slots=occupied_slots_enriched,
        available_slots=available_blocks
    )
