from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from app.db.session import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, index=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, index=True, nullable=False)
    passport = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔥 ДОБАВЛЕНО!
    
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")