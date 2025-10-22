from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Reservation, Locale
from ..database import async_session, get_async_session
from ..dependencies import get_current_user, get_async_session
from ..schemas import ReservationOut, ReservationWithLocaleOut, ReservationStatusUpdate, LocaleOut
from ..enums import UserRole, ReservationStatus
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, time
from typing import List

router = APIRouter()

@router.get("/conflicts")
async def list_overlapping():
    """
    Devuelve todas las reservas 'pending' que se solapan en mismo local y horario.
    """
    async with async_session() as session:
        pending = await session.execute(select(Reservation).filter(Reservation.status == "pending"))
        pending = pending.scalars().all()

    conflicts = []
    for r in pending:
        async with async_session() as session:
            overlap = await session.execute(
                select(Reservation).filter(
                    Reservation.locale_id == r.locale_id,
                    Reservation.id != r.id,
                    Reservation.status == "pending",
                    Reservation.start_dt < r.end_dt,
                    Reservation.end_dt > r.start_dt
                )
            )
            if overlap.scalars().first():
                conflicts.append(r)
    return conflicts


@router.post("/resolve/{reservation_id}")
async def resolve(reservation_id: str, priority: int, status: str):
    """
    Asigna prioridad y estado (approved/rejected) a una reserva.
    """
    async with async_session() as session:
        res = await session.get(Reservation, reservation_id)
        if not res:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        res.priority = priority
        res.status = status
        await session.commit()
    return {"msg": "Resolución guardada"}

@router.get("/reservations/pending", response_model=list[dict])
async def pending_reservations(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "No autorizado")
    async with async_session() as session:
        stmt = (
            select(Reservation)
            .options(joinedload(Reservation.locale))  # ← carga el local
            .where(Reservation.status == ReservationStatus.pending)
            .order_by(Reservation.start_dt)
        )
        rows = (await session.execute(stmt)).scalars().all()

        # ← armamos el DTO a mano
        return [
            {
                "id": str(r.id),
                "startDate": r.start_dt.isoformat(),
                "endDate": r.end_dt.isoformat(),
                "status": r.status.value,
                "motive": r.motive,
                "userName": r.user.full_name if r.user else "Usuario Desconocido",
                "userEmail": r.user.email if r.user else "Sin email",
                "locale": {
                    "id": str(r.locale_id),
                    "name": r.locale.name if r.locale else "Local Desconocido",
                    "imagen_url": f"/assets/locales/{r.locale.imagen}" if r.locale.imagen else "/assets/img/no-image.jpg"
                }
            }
            for r in rows
        ]

@router.patch("/reservations/{res_id}/status", response_model=ReservationOut)
async def set_reservation_status(
    res_id: str,
    # Se recomienda renombrar el parámetro para evitar confusión.
    # Lo llamaremos 'status_update' para indicar que es el objeto Pydantic.
    status_update: ReservationStatusUpdate,  
    current_user=Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")
        
    # Extraemos el valor del Enum del objeto Pydantic
    new_status_value = status_update.status 

    async with async_session() as session:
        res = await session.execute(select(Reservation).where(Reservation.id == res_id))
        reservation = res.scalar_one_or_none()
        
        if not reservation:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
            
        # 🛠️ CORRECCIÓN CLAVE: Asignamos el valor extraído (new_status_value), 
        # que es un objeto Enum, no el modelo Pydantic completo.
        reservation.status = new_status_value 
        
        await session.commit()
        await session.refresh(reservation)
        return reservation

# ====================================================================
# 🔒 ENDPOINT DE ADMINISTRADOR: HISTORIAL DE TODAS LAS RESERVAS
# ====================================================================
# ⚠️ IMPORTANTE: Este endpoint asume que solo el administrador puede acceder a él.
# La lógica de autorización debe estar en get_current_user (o un nuevo Depends).
# Por ahora, solo requiere autenticación.

@router.get("/history", response_model=list[dict])
async def get_all_history_reservations(
    start_date: str | None = Query(None, alias="start_date"),
    end_date: str | None = Query(None, alias="end_date"),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Obtiene TODAS las reservas (cualquier estado) con su información completa.
    Solo accesible por administradores.
    """
    # 1. Construcción de la consulta con JOINs
    stmt = select(Reservation).options(
        selectinload(Reservation.locale),
        selectinload(Reservation.user)
    )

    # 2. (Opcional) filtros de rango de fecha si los mandan
    try:
        if start_date:
            start_dt_parsed = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            stmt = stmt.where(Reservation.start_dt >= start_dt_parsed.replace(tzinfo=None))

        if end_date:
            end_dt_parsed = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            stmt = stmt.where(Reservation.start_dt <= end_dt_parsed.replace(tzinfo=None))
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use ISO 8601.")

    # 3. Ordenar por fecha (más reciente primero)
    stmt = stmt.order_by(desc(Reservation.start_dt))

    # 4. Ejecutar la consulta
    res = await session.execute(stmt)
    reservations = res.scalars().all()

    # 5. Mapear el resultado
    return [
        {
            "id": str(r.id),
            "startDate": r.start_dt.isoformat(),
            "endDate": r.end_dt.isoformat(),
            "status": r.status.value,
            "motive": r.motive,
            "userName": r.user.full_name if r.user else "Usuario Desconocido",
            "userEmail": r.user.email if r.user else "Sin email",
            "locale": {
                "id": str(r.locale_id),
                "name": r.locale.name if r.locale else "Local Desconocido",
                "imagen_url": f"/assets/locales/{r.locale.imagen}" if r.locale.imagen else "/assets/img/no-image.jpg"
            }
        }
        for r in reservations
    ]

# ---------- LISTAR ----------
@router.get("/locales", response_model=list[LocaleOut])
async def list_locales(current_user=Depends(get_current_user),
                       session: AsyncSession = Depends(get_async_session)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")

    rows = (await session.execute(select(Locale).order_by(Locale.name))).scalars().all()

    return [
        LocaleOut(
            id=str(r.id),
            name=r.name,
            description=r.description,
            capacity=r.capacity,
            location=r.location,
            open_time=r.open_time.strftime("%H:%M"),
            close_time=r.close_time.strftime("%H:%M"),
            imagen_url=f"/assets/locales/{r.imagen}" if r.imagen else "/assets/img/no-image.jpg"
        )
        for r in rows
    ]

# ---------- CREAR ----------
@router.post("", response_model=LocaleOut)
async def create_locale(
    name: str = Form(...),
    description: str = Form(...),
    capacity: int = Form(...),
    location: str = Form(...),
    open_time: str = Form(...),
    close_time: str = Form(...),
    imagen: UploadFile | None = File(None),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")

    file_name = imagen.filename if imagen else None
    if imagen:
        with open(f"frontend/src/assets/locales/{file_name}", "wb") as f:
            f.write(imagen.file.read())

    new_locale = Locale(
        name=name,
        description=description,
        capacity=capacity,
        location=location,
        open_time=open_time,
        close_time=close_time,
        imagen=file_name
    )
    session.add(new_locale)
    await session.commit()
    await session.refresh(new_locale)
    return new_locale

# ---------- EDITAR ----------
@router.patch("/{locale_id}", response_model=LocaleOut)
async def update_locale(
    locale_id: str,
    name: str = Form(...),
    description: str = Form(...),
    capacity: int = Form(...),
    location: str = Form(...),
    open_time: str = Form(...),
    close_time: str = Form(...),
    imagen: UploadFile | None = File(None),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")

    res = await session.get(Locale, locale_id)
    if not res:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    # actualizar campos
    for field, value in {"name": name, "description": description, "capacity": capacity, "location": location, "open_time": open_time, "close_time": close_time}.items():
        setattr(res, field, value)

    # imagen opcional
    if imagen:
        file_name = imagen.filename
        with open(f"frontend/src/assets/locales/{file_name}", "wb") as f:
            f.write(imagen.file.read())
        res.imagen = file_name

    await session.commit()
    await session.refresh(res)
    return res

# ---------- ELIMINAR ----------
@router.delete("/{locale_id}", status_code=204)
async def delete_locale(locale_id: str,
                        current_user=Depends(get_current_user),
                        session: AsyncSession = Depends(get_async_session)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")
    res = await session.get(Locale, locale_id)
    if not res:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    await session.delete(res)
    await session.commit()