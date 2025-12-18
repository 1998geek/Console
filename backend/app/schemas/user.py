from pydantic import BaseModel

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
