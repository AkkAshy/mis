from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime
from app.db.session import get_db
from app.schemas.queue import QueueCreate, Queue as QueueSchema, QueueListResponse, QueueWithPatient
from app.models.queue import Queue as QueueModel
from app.models.patient import Patient as PatientModel
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=QueueSchema)
def add_patient_to_queue(
    queue_data: QueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Добавление пациента в очередь врача (FIFO - новые пациенты добавляются в конец).
    """
    today = date.today()

    # Проверяем, существует ли пациент
    patient = db.query(PatientModel).filter(PatientModel.id == queue_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Проверяем, существует ли врач
    doctor = db.query(User).filter(User.id == queue_data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Проверяем, не находится ли пациент уже в очереди у этого врача сегодня
    existing = db.query(QueueModel).filter(
        and_(
            QueueModel.patient_id == queue_data.patient_id,
            QueueModel.doctor_id == queue_data.doctor_id,
            QueueModel.queue_date == today
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Patient already in queue for this doctor today")

    # FIFO: Находим максимальный номер в очереди
    max_queue = db.query(func.max(QueueModel.queue_number)).filter(
        and_(
            QueueModel.doctor_id == queue_data.doctor_id,
            QueueModel.queue_date == today
        )
    ).scalar()

    # Новый пациент получает следующий номер (max + 1, или 1 если очередь пустая)
    next_queue_number = (max_queue or 0) + 1

    new_queue_entry = QueueModel(
        patient_id=queue_data.patient_id,
        doctor_id=queue_data.doctor_id,
        queue_number=next_queue_number,
        queue_date=today
    )

    db.add(new_queue_entry)
    db.commit()
    db.refresh(new_queue_entry)

    return new_queue_entry


@router.get("/doctor/{doctor_id}", response_model=QueueListResponse)
def get_doctor_queue(
    doctor_id: int,
    queue_date: Optional[date] = Query(None, description="Date of queue (default: today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение очереди для конкретного врача на определенную дату.
    По умолчанию показывает сегодняшнюю очередь.
    """
    if queue_date is None:
        queue_date = date.today()

    # Получаем очередь с информацией о пациентах
    queue_entries = db.query(
        QueueModel,
        PatientModel.full_name,
        PatientModel.phone
    ).join(
        PatientModel, QueueModel.patient_id == PatientModel.id
    ).filter(
        and_(
            QueueModel.doctor_id == doctor_id,
            QueueModel.queue_date == queue_date
        )
    ).order_by(QueueModel.queue_number).all()

    # Формируем ответ
    queue_list = []
    for queue_entry, patient_name, patient_phone in queue_entries:
        queue_list.append({
            "id": queue_entry.id,
            "patient_id": queue_entry.patient_id,
            "doctor_id": queue_entry.doctor_id,
            "queue_number": queue_entry.queue_number,
            "queue_date": queue_entry.queue_date,
            "created_at": queue_entry.created_at,
            "patient_full_name": patient_name,
            "patient_phone": patient_phone
        })

    return QueueListResponse(queue=queue_list, total_count=len(queue_list))


@router.delete("/{queue_id}")
def remove_from_queue(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление пациента из очереди.
    После удаления номера всех следующих пациентов уменьшаются на 1.
    """
    queue_entry = db.query(QueueModel).filter(QueueModel.id == queue_id).first()
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    removed_number = queue_entry.queue_number
    doctor_id = queue_entry.doctor_id
    queue_date = queue_entry.queue_date

    # Удаляем запись
    db.delete(queue_entry)

    # Пересчитываем номера для всех, кто был после удаленного
    db.query(QueueModel).filter(
        and_(
            QueueModel.doctor_id == doctor_id,
            QueueModel.queue_date == queue_date,
            QueueModel.queue_number > removed_number
        )
    ).update({"queue_number": QueueModel.queue_number - 1})

    db.commit()

    return {"message": "Patient removed from queue successfully"}


@router.post("/clear/{doctor_id}")
def clear_doctor_queue(
    doctor_id: int,
    queue_date: Optional[date] = Query(None, description="Date of queue to clear (default: today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Очистка очереди врача на определенную дату.
    """
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    if queue_date is None:
        queue_date = date.today()

    deleted_count = db.query(QueueModel).filter(
        and_(
            QueueModel.doctor_id == doctor_id,
            QueueModel.queue_date == queue_date
        )
    ).delete()

    db.commit()

    return {"message": f"Queue cleared successfully. Removed {deleted_count} entries."}


@router.post("/reset-all")
def reset_all_queues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Сброс всех очередей за сегодня (для автоматического вызова в 00:00).
    Доступно только для администраторов.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    today = date.today()
    deleted_count = db.query(QueueModel).filter(QueueModel.queue_date < today).delete()

    db.commit()

    return {"message": f"All old queues cleared successfully. Removed {deleted_count} entries."}
