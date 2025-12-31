from pydantic import BaseModel, EmailStr
from datetime import datetime

# ----- User Schemas -----
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True

# ----- Token Schemas -----
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
