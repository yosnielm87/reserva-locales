from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, sql, Enum 
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from .enums import UserRole # Recomiendo usar importación relativa si están en el mismo paquete.

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(
        # Opción A: Usar String y values_callable (Recomendado para PostgreSQL)
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x], create_type=False),
        #                                                           ^^^^^^^
        # El .value ya está en minúsculas ('user'), y lo enviamos como string.
        # create_type=False asume que ya existe en la BD.
        
        # O la forma más sencilla si tu BD está bien:
        # String,
        
        default=UserRole.USER, 
        nullable=False
    )
    is_active = Column(Boolean, default=True)

class Locale(Base):
	__tablename__ = "locales"        # ← faltaba
	id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
	name = Column(String, nullable=False)
	description = Column(Text)
	capacity = Column(Integer)
	location = Column(String)
	open_time = Column(String)
	close_time = Column(String)
	active = Column(Boolean, default=True)

class Reservation(Base):
	__tablename__ = "reservations"   # ← faltaba
	id = Column(UUID(as_uuid=True), primary_key=True, server_default=sql.text("uuid_generate_v4()"))
	locale_id = Column(UUID(as_uuid=True), ForeignKey("locales.id"))
	user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
	start_dt = Column(DateTime, nullable=False)
	end_dt = Column(DateTime, nullable=False)
	motive = Column(Text)
	status = Column(String, server_default="pending")
	priority = Column(Integer, server_default="9")