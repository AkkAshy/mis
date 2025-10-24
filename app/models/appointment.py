from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=True))
    status = Column(String, default="scheduled")  # scheduled, arrived, in_progress, done
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    doctor = relationship("User", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

    def finish(self):
        self.status = "done"

    def __repr__(self):
        return f"Appointment(id={self.id}, doctor_id={self.doctor_id}, patient_id={self.patient_id}, date={self.date}, status={self.status}, notes={self.notes})"