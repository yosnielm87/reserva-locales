#backend/app/enums.py
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ReservationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"