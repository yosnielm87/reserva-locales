from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .database import async_session
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = "super-secret-jwt-key-change-me"
ALGORITHM = "HS256"
async def get_current_user(token: str = Depends(oauth2_scheme)):
credentials_exception = HTTPException(
status_code=status.HTTP_401_UNAUTHORIZED,
detail="Credenciales inválidas",
headers={"WWW-Authenticate": "Bearer"},
)
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
email: str = payload.get("sub")
if email is None:
raise credentials_exception
except JWTError:
raise credentials_exception
async with async_session() as session:
user = await session.execute(select(User).where(User.email == email))
user = user.scalars().first()
if user is None:
raise credentials_exception
return user