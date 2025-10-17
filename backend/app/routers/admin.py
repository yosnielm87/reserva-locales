from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Reservation
from ..database import async_session
from ..dependencies import get_current_user
from ..schemas import ReservationOut
from ..enums import UserRole, ReservationStatus
from sqlalchemy.orm import joinedload
from ..schemas import ReservationWithLocaleOut

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

@router.get("/reservations/pending", response_model=list[ReservationWithLocaleOut])
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
                **r.__dict__,
                "locale_name": r.locale.name
            }
            for r in rows
        ]


@router.patch("/reservations/{res_id}/status")
async def set_reservation_status(
    res_id: str,
    status: ReservationStatus,
    current_user=Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No autorizado")
    async with async_session() as session:
        res = await session.execute(select(Reservation).where(Reservation.id == res_id))
        reservation = res.scalar_one_or_none()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        reservation.status = status
        await session.commit()
        return {"msg": "Estado actualizado"}