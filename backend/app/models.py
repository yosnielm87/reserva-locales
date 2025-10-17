#backend/app/models.py
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey, sql
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Enum as SAEnum  # ← importamos el de SQLA
from .enums import UserRole, ReservationStatus


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(
        # Opción A: Usar String y values_callable (Recomendado para PostgreSQL)
        SAEnum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x], create_type=False),
        #                                                           ^^^^^^^
        # El .value ya está en minúsculas ('user'), y lo enviamos como string.
        # create_type=False asume que ya existe en la BD.
        
        # O la forma más sencilla si tu BD está bien:
        # String,
        
        default=UserRole.USER, 
        nullable=False
    )
    is_active = Column(Boolean, default=True)

    # ⬇️⬇️  Relación inversa  ⬇️⬇️
    reservations = relationship("Reservation", back_populates="user")

class Locale(Base):
    __tablename__ = "locales"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
    name = Column(String, nullable=False)
    description = Column(Text)
    capacity = Column(Integer)
    location = Column(String)
    open_time = Column(String)
    close_time = Column(String)
    active = Column(Boolean, default=True)

    # ⬇️ 4 espacios exactos ⬇️
    reservations = relationship("Reservation", back_populates="locale")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
    locale_id = Column(UUID(as_uuid=True), ForeignKey("locales.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_dt = Column(DateTime, nullable=False)
    end_dt = Column(DateTime, nullable=False)
    motive = Column(Text)
    status = Column(
        SAEnum(ReservationStatus, name="reservation_status", create_type=False),
        nullable=False,
        server_default=sql.text("'pending'::reservation_status")
    )
    priority = Column(Integer, server_default=sql.text("9"))

    # ⬇️⬇️  Relaciones  ⬇️⬇️
    locale = relationship("Locale", back_populates="reservations", lazy="joined")
    user = relationship("User", back_populates="reservations", lazy="joined")