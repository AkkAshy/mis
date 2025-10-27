from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date: datetime
    notes: Optional[str] = None
    cost: Optional[Decimal] = None  # Reception может оставить пустым, doctor может установить

class AppointmentWithDoctor(BaseModel):
    id: int
    patient_full_name: Optional[str]
    doctor_id: int
    patient_id: int
    date: datetime
    status: str
    notes: Optional[str] = None
    cost: Optional[Decimal] = None

    class Config:
        from_attributes = True

class Appointment(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: datetime
    status: str
    notes: Optional[str] = None
    cost: Optional[Decimal] = None

    class Config:
        from_attributes = True

class AppointmentStatusUpdate(BaseModel):
    status: str  # можно только "done" или "in_progress"

class AppointmentCostUpdate(BaseModel):
    cost: Decimal  # Стоимость приема, устанавливаемая доктором