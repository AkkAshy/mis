from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_uid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    full_name = Column(String, index=True)
    birth_date = Column(Date)
    gender = Column(String)
    phone = Column(String, index=True)
    passport = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)