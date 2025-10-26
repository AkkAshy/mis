from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, Appointment, AppointmentWithDoctor
from app.schemas.patient import Patient
from app.schemas.user import UserProfile
from app.models.appointment import Appointment as AppointmentModel
from app.models.patient import Patient as PatientModel
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Appointment)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")
    # Check if doctor is available at that time
    existing_appointment = db.query(AppointmentModel).filter(
        AppointmentModel.doctor_id == appointment.doctor_id,
        AppointmentModel.date == appointment.date,
        
    ).first()
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time")
    db_appointment = AppointmentModel(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/doctors/", response_model=List[UserProfile])
def get_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")
    doctors = db.query(User).filter(User.role == "doctor").all()
    return doctors

@router.get("/my", response_model=List[AppointmentWithDoctor])
def get_my_appointments(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(AppointmentModel, User.username.label("doctor_name")).join(
        User, AppointmentModel.doctor_id == User.id
    ).filter(AppointmentModel.doctor_id == current_user.id)
    if status:
        query = query.filter(AppointmentModel.status == status)
    results = query.all()
    appointments = []
    for appointment, doctor_name in results:
        appointment_data = AppointmentWithDoctor.from_orm(appointment)
        appointment_data.doctor_name = doctor_name
        appointments.append(appointment_data)
    return appointments

@router.patch("/my/{appointment_id}/finish", response_model=Appointment)
def finish_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can finish appointments")

    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.id == appointment_id,
        AppointmentModel.doctor_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "done"
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/patients/{patient_id}", response_model=Patient)
def get_patient_details(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    # Check if the patient is assigned to this doctor
    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.patient_id == patient_id,
        AppointmentModel.doctor_id == current_user.id
    ).first()
    if not appointment:
        raise HTTPException(status_code=403, detail="Patient not assigned to this doctor")
    patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient