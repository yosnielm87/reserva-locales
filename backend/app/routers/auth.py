from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from ..models import User
from ..schemas import UserCreate, Token
from ..database import async_session
from ..dependencies import get_current_user
router = APIRouter()
SECRET_KEY = "super-secret-jwt-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
def create_access_token(data: dict, expires_delta: timedelta = None):
to_encode = data.copy()
expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
to_encode.update({"exp": expire})
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
@router.post("/register", response_model=Token)
async def register(user: UserCreate):
async with async_session() as session:
res = await session.execute(select(User).where(User.email == user.email))
if res.scalars().first():
raise HTTPException(status_code=400, detail="Email ya registrado")
new_user = User(
email=user.email,
password_hash=bcrypt.hash(user.password),
full_name=user.full_name,
role="user"
)
session.add(new_user)
await session.commit()
access_token = create_access_token(data={"sub": user.email, "role": "user"})
return {"access_token": access_token, "token_type": "bearer"}
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
async with async_session() as session:
res = await session.execute(select(User).where(User.email == form_data.username))
user = res.scalars().first()
if not user or not bcrypt.verify(form_data.password, user.password_hash):
raise HTTPException(status_code=400, detail="Credenciales incorrectas")
access_token = create_access_token(data={"sub": user.email, "role": user.role})
return {"access_token": access_token, "token_type": "bearer"}
@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
return {"email": current_user.email, "full_name": current_user.full_name, "role": current_user.role}