from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from ..models import Reservation, Locale
from ..schemas import ReservationCreate, ReservationOut
from ..database import async_session
from ..dependencies import get_current_user
router = APIRouter()
@router.post("/", response_model=ReservationOut)
async def create_reservation(
data: ReservationCreate,
current_user=Depends(get_current_user)
):
async with async_session() as session:
locale = await session.get(Locale, data.locale_id)
if not locale:
raise HTTPException(status_code=404, detail="Local no encontrado")
new_res = Reservation(
locale_id=data.locale_id,
user_id=current_user.id,
start_dt=data.start_dt,
end_dt=data.end_dt,
motive=data.motive,
status="pending",
priority=9
)
session.add(new_res)
await session.commit()
await session.refresh(new_res)
return new_res
@router.get("/my", response_model=list[ReservationOut])
async def my_reservations(current_user=Depends(get_current_user)):
async with async_session() as session:
res = await session.execute(
select(Reservation).where(Reservation.user_id == current_user.id)
)
return res.scalars().all()