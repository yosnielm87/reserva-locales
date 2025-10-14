from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
class UserCreate(BaseModel):
email: EmailStr
password: str
full_name: str
class Token(BaseModel):
access_token: str
token_type: str
class LocaleOut(BaseModel):
id: UUID
name: str
description: str
capacity: int
location: str
open_time: str
close_time: str
active: bool

class Config:
    from_attributes = True

class ReservationCreate(BaseModel):
locale_id: UUID
start_dt: datetime
end_dt: datetime
motive: str
class ReservationOut(BaseModel):
id: UUID
locale_id: UUID
user_id: UUID
start_dt: datetime
end_dt: datetime
motive: str
status: str
priority: int

class Config:
    from_attributes = True

