from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Asegúrate de que tu async_session esté correctamente importada y sea un SessionMaker
from .database import async_session 
from .models import User

# --- Configuración de Seguridad ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = "super-secret-jwt-key-change-me"
ALGORITHM = "HS256"

# =======================================================
# 1. FUNCIÓN DE DEPENDENCIA PARA SESIÓN DB (AÑADIDA)
# =======================================================
async def get_async_session() -> AsyncSession:
    """Proporciona una sesión de base de datos asíncrona para las dependencias."""
    # Nota: Tu async_session debe ser la factoría (SessionMaker)
    async with async_session() as session:
        yield session

# =======================================================
# 2. FUNCIÓN DE DEPENDENCIA PARA USUARIO ACTUAL (ORIGINAL)
# =======================================================
async def get_current_user(session: AsyncSession = Depends(get_async_session), # ⬅️ Usa la nueva dependencia aquí
                           token: str = Depends(oauth2_scheme)):
    
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
    
    # Usa la sesión inyectada por la dependencia get_async_session
    user = await session.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    return user
