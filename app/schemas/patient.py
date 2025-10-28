from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

class PatientCreate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    phone: str
    passport: Optional[str] = None
    address: Optional[str] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    passport: Optional[str] = None
    address: Optional[str] = None

class Patient(BaseModel):
    id: int
    patient_uid: UUID
    full_name: str
    birth_date: date
    gender: str
    phone: str
    passport: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    patients: List[Patient]
    total_count: int