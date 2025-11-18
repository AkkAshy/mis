from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
import uuid
import logging
import traceback
from datetime import date
from app.db.session import get_db
from app.schemas.patient import PatientCreate, Patient, PatientUpdate, PatientListResponse
from app.models.patient import Patient as PatientModel
from app.models.queue import Queue as QueueModel
from app.utils.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

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
    doctor_id: Optional[int] = Query(None, description="Filter by doctor queue"),
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

    # LIFO - сортируем по ID в обратном порядке (последний зарегистрированный первым)
    query = query.order_by(PatientModel.id.desc())

    total_count = query.count()
    patients_db = query.offset(skip).limit(limit).all()

    # Получаем информацию об очереди для каждого пациента (если указан doctor_id)
    patients = []
    today = date.today()

    for patient in patients_db:
        patient_dict = {
            "id": patient.id,
            "patient_uid": patient.patient_uid,
            "full_name": patient.full_name,
            "birth_date": patient.birth_date,
            "gender": patient.gender,
            "phone": patient.phone,
            "passport": patient.passport,
            "address": patient.address,
            "created_at": patient.created_at,
            "queue_number": None
        }

        # Если указан doctor_id, получаем номер очереди пациента у этого врача
        if doctor_id:
            queue_entry = db.query(QueueModel).filter(
                and_(
                    QueueModel.patient_id == patient.id,
                    QueueModel.doctor_id == doctor_id,
                    QueueModel.queue_date == today
                )
            ).first()

            if queue_entry:
                patient_dict["queue_number"] = queue_entry.queue_number

        patients.append(patient_dict)

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
    try:
        logger.info(f"🗑️ Attempting to delete patient {patient_id} by user {current_user.username}")

        if current_user.role != "reception":
            logger.warning(f"⚠️ User {current_user.username} not authorized to delete patients")
            raise HTTPException(status_code=403, detail="Not authorized")

        patient = db.query(PatientModel).filter(PatientModel.id == patient_id).first()
        if not patient:
            logger.warning(f"⚠️ Patient {patient_id} not found")
            raise HTTPException(status_code=404, detail="Patient not found")

        patient_name = patient.full_name
        logger.info(f"📝 Deleting patient: {patient_name} (ID: {patient_id})")

        db.delete(patient)
        db.commit()

        logger.info(f"✅ Patient {patient_id} deleted successfully")
        return {"message": "Patient deleted successfully", "patient_id": patient_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting patient {patient_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")