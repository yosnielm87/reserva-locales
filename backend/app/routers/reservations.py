from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy.future import select, desc
from sqlalchemy import select, desc
from datetime import datetime, time, timedelta
# Asegúrate de que los modelos y esquemas están correctamente importados
from ..models import Reservation, Locale, ReservationStatus 
from ..schemas import ReservationCreate, ReservationOut
# Asumo que get_async_session reemplaza async_session en las dependencias
from ..dependencies import get_current_user, get_async_session 
# from ..database import async_session 

router = APIRouter(
    # prefix="/reservations",
    tags=["reservations"]
)

# ====================================================================
# 🚀 CREACIÓN DE RESERVA (CON VALIDACIÓN DE HORARIO Y CORRECCIÓN DE DATETIME)
# ====================================================================

@router.post("/", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationCreate,
    current_user=Depends(get_current_user),
    # Cambié el uso de async_session() as session por una dependencia para mejor integración con FastAPI
    session: AsyncSession = Depends(get_async_session) 
):
    """
    Crea una nueva reserva (estado pendiente por defecto) validando que esté dentro del horario del local.
    """

    # 1. ⚠️ CORRECCIÓN CLAVE: Hacer los datetimes 'naive' (sin zona horaria)
    # Esto resuelve el error "can't subtract offset-naive and offset-aware datetimes" en PostgreSQL.
    start_dt_naive = data.start_dt.replace(tzinfo=None)
    end_dt_naive = data.end_dt.replace(tzinfo=None)
    
    # 2. Validación básica: la hora de inicio debe ser anterior a la de fin
    if start_dt_naive >= end_dt_naive:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser anterior a la hora de fin.")

    # 3. Verificar Local
    locale = await session.get(Locale, data.locale_id)
    if not locale or not locale.active:
        raise HTTPException(status_code=404, detail="Local no encontrado o inactivo.")

    # 4. Verificar Horario de Operación del Local (Lógica de horarios)
    
    # Intenta convertir open_time/close_time a objetos time si son strings (como es común en modelos)
    try:
        if isinstance(locale.open_time, time):
            open_t = locale.open_time
            close_t = locale.close_time
        else:
            open_t = datetime.strptime(str(locale.open_time), "%H:%M:%S").time() # Asumiendo formato HH:MM:SS
            close_t = datetime.strptime(str(locale.close_time), "%H:%M:%S").time()
    except (ValueError, TypeError):
        raise HTTPException(status_code=500, detail="Horario del local mal configurado en la base de datos.")
    
    # Combina la fecha de la reserva con los horarios del local para crear rangos Naive
    reservation_date = start_dt_naive.date()
    locale_start_dt = datetime.combine(reservation_date, open_t)
    locale_end_dt_time = datetime.combine(reservation_date, close_t)
    
    # Manejar cierre al día siguiente (ej: 22:00 a 06:00)
    if locale_end_dt_time <= locale_start_dt:
        locale_end_dt = locale_end_dt_time + timedelta(days=1)
    else:
        locale_end_dt = locale_end_dt_time

    # La comparación ahora es válida porque todos los datetimes son Naive
    if not (locale_start_dt <= start_dt_naive and end_dt_naive <= locale_end_dt):
        raise HTTPException(status_code=400, detail=f"La reserva está fuera del horario de operación del local ({open_t.strftime('%H:%M')} a {close_t.strftime('%H:%M')}).")

    # 5. Crear y Guardar la Reserva
    new_res = Reservation(
        locale_id=data.locale_id,
        user_id=current_user.id,
        start_dt=start_dt_naive, # ⬅️ USAR LA VERSIÓN NAIVE
        end_dt=end_dt_naive,     # ⬅️ USAR LA VERSIÓN NAIVE
        motive=data.motive,
        status=ReservationStatus.pending, # Usar el Enum si está disponible
        priority=9
    )
    
    session.add(new_res)
    await session.commit()
    await session.refresh(new_res)
    return new_res

# ====================================================================
# 📚 OBTENER MIS RESERVAS
# ====================================================================

from datetime import datetime

@router.get("/my", response_model=list[ReservationOut])
async def my_reservations(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Reservas del usuario a partir de hoy (futuras)."""
    stmt = (
        select(Reservation)
        .where(
            Reservation.user_id == current_user.id,
            Reservation.start_dt >= datetime.utcnow()
        )
        .order_by(Reservation.start_dt)
    )
    res = await session.execute(stmt)
    return res.scalars().all()

@router.get("/my/history", response_model=list[ReservationOut])
async def my_history(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Reservas PASADAS del usuario autenticado."""
    stmt = (
        select(Reservation)
        .where(
            Reservation.user_id == current_user.id,
            Reservation.start_dt < datetime.utcnow()
        )
        .order_by(desc(Reservation.start_dt))  # más reciente primero
    )
    res = await session.execute(stmt)
    return res.scalars().all()