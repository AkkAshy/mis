from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date: datetime
    notes: Optional[str] = None

class AppointmentWithDoctor(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: datetime
    status: str
    notes: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True

class Appointment(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: datetime
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class AppointmentStatusUpdate(BaseModel):
    status: str  # можно только "done" или "in_progress"