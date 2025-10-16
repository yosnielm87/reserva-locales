# backend/app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 🚨 NUEVA IMPORTACIÓN: Necesitas la clase Pool
from sqlalchemy.pool import Pool 
from sqlalchemy import event, DDL 

# Asumo que la importación de UserRole es correcta y la dejo aquí
# Si UserRole no es necesario en database.py, puedes borrar esta línea.
from .enums import UserRole 

# Cargar variables de entorno
load_dotenv()

# Leer la URL desde el .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine y sesión
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()

# -------------------------------------------------------------
# 🛠️ CORRECCIÓN: La función para el evento 'connect' debe ser SÍNCRONA
# -------------------------------------------------------------

def register_enum_types_sync(dbapi_connection, connection_record):
    """
    Función síncrona que se ejecuta al conectar. 
    Asegura que asyncpg mapee el tipo ENUM de PostgreSQL.
    """
    # 1. Obtener la conexión base de asyncpg
    # La conexión dbapi_connection es un envoltorio (wrapper) de SQLAlchemy.
    # Necesitamos el objeto de conexión de asyncpg real.
    asyncpg_conn = dbapi_connection.connection

    # 2. Registrar el tipo ENUM directamente en la conexión asyncpg.
    # El dialecto de SQLAlchemy/asyncpg ya sabe cómo manejar el tipo ENUM
    # si se le proporciona la clase Python.
    from .enums import UserRole # Re-importar si es necesario dentro de la función, 
                                # aunque ya debería estar al principio del archivo.
                                
    asyncpg_conn.driver_connection.set_type_codec(
        "user_role", 
        encoder=UserRole, 
        decoder=UserRole, 
        format='text'
    )