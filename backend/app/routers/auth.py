# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
import bcrypt as bcrypt_native
from jose import jwt
from datetime import datetime, timedelta
from ..models import User
from ..schemas import UserCreate, Token
from ..database import async_session
from ..dependencies import get_current_user
from ..enums import UserRole

router = APIRouter()

SECRET_KEY = "super-secret-jwt-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


# ✅ Wrapper propio: mismo nombre para no tocar el resto del código
class pwd_context:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt_native.hashpw(
            password.encode('utf-8')[:72],
            bcrypt_native.gensalt()
        ).decode('utf-8')

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return bcrypt_native.checkpw(
            password.encode('utf-8')[:72],
            hashed.encode('utf-8')
        )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=Token, status_code=201)
async def register(user: UserCreate):
    async with async_session() as session:
        # 1. ¿Existe el email?
        res = await session.execute(select(User).where(User.email == user.email))
        if res.scalars().first():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        # 2. Creamos el usuario
        new_user = User(
            email=user.email,
            password_hash=pwd_context.hash(user.password),
            full_name=user.full_name,
            role=UserRole.USER
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)          # <- trae id y role definitivos

    # 3. Token para el usuario recién creado
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role}
    )

    # 4. Lo devolvemos tal como espera el esquema Token
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with async_session() as session:
        res = await session.execute(select(User).where(User.email == form_data.username))
        user = res.scalars().first()
        if not user:
            raise HTTPException(status_code=400, detail="Credenciales incorrectas")

        if not pwd_context.verify(form_data.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "full_name": current_user.full_name, "role": current_user.role}