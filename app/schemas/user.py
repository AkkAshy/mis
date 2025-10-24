from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    role: str  # 'reception' or 'doctor'

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None