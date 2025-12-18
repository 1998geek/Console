from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    email: str | None = None

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    username: str
    email: str | None = None
    created_at: datetime | None = None
    is_admin: bool

    class Config:
        from_attributes = True
