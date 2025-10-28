from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.db.session import get_db
from app.schemas.patient import PatientCreate, Patient, PatientUpdate, PatientListResponse
from app.models.patient import Patient as PatientModel
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Patient)
def create_patient(
    patient: PatientCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Проверка на дубликаты
    db_patient = db.query(PatientModel).filter(
        PatientModel.full_name == patient.full_name,
        PatientModel.birth_date == patient.birth_date
    ).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    # UUID генерируется автоматически в модели
    db_patient = PatientModel(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=PatientListResponse)
def search_patients(
    search: Optional[str] = Query(None, description="Search by name"),
    phone: Optional[str] = Query(None, description="Search by phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(PatientModel)

    if search:
        query = query.filter(PatientModel.full_name.ilike(f"%{search}%"))
    if phone:
        query = query.filter(PatientModel.phone.contains(phone))

    total_count = db.query(PatientModel).count()
    patients = query.offset(skip).limit(limit).all()

    return PatientListResponse(patients=patients, total_count=total_count)

@router.get("/{patient_id}", response_model=Patient)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.patch("/{patient_id}", response_model=Patient)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")

    patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")

    patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}