from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Locale
from ..schemas import LocaleOut
from ..database import async_session
router = APIRouter()

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