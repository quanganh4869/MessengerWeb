from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True