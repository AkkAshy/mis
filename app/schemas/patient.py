from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class PatientCreate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    phone: str
    passport: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None

class Patient(BaseModel):
    id: int
    patient_uid: UUID
    full_name: str
    birth_date: date
    gender: str
    phone: str
    passport: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True