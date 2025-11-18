from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class QueueBase(BaseModel):
    patient_id: int
    doctor_id: int

class QueueCreate(QueueBase):
    pass

class Queue(QueueBase):
    id: int
    queue_number: int
    queue_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class QueueWithPatient(Queue):
    patient_full_name: str
    patient_phone: str

class QueueListResponse(BaseModel):
    queue: List[QueueWithPatient]
    total_count: int
