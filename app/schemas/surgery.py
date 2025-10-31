from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

class SurgeryCreate(BaseModel):
    patient_id: int
    surgeon_id: int
    operation_name: str = Field(..., max_length=255)
    operation_date: datetime
    start_time: datetime
    end_time: Optional[datetime] = None
    pre_op_days: Optional[int] = None
    post_op_days: Optional[int] = None
    notes: Optional[str] = None
    complications: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class SurgeryUpdate(BaseModel):
    operation_name: Optional[str] = Field(None, max_length=255)
    operation_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pre_op_days: Optional[int] = None
    post_op_days: Optional[int] = None
    notes: Optional[str] = None
    complications: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class Surgery(BaseModel):
    id: int
    patient_id: int
    surgeon_id: int
    operation_name: str
    operation_date: datetime
    start_time: datetime
    end_time: Optional[datetime] = None
    pre_op_days: Optional[int] = None
    post_op_days: Optional[int] = None
    notes: Optional[str] = None
    complications: Optional[str] = None
    outcome: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SurgeryWithDetails(BaseModel):
    id: int
    patient_id: int
    patient_full_name: Optional[str]
    surgeon_id: int
    surgeon_full_name: Optional[str]
    operation_name: str
    operation_date: datetime
    start_time: datetime
    end_time: Optional[datetime] = None
    pre_op_days: Optional[int] = None
    post_op_days: Optional[int] = None
    notes: Optional[str] = None
    complications: Optional[str] = None
    outcome: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True