from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from app.db.session import Base

class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    queue_number = Column(Integer, nullable=False)  # Номер в очереди (1, 2, 3...)
    queue_date = Column(Date, nullable=False, default=date.today)  # Дата очереди
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", backref="queue_entries")
    doctor = relationship("User", backref="queue_entries")
