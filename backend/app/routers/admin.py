from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Reservation
from ..database import async_session
from ..dependencies import get_current_user

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