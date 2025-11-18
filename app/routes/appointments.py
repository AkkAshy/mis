from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date as date_type
from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, Appointment, AppointmentWithDoctor, AppointmentCostUpdate
from app.schemas.patient import Patient
from app.schemas.user import UserProfile
from app.models.appointment import Appointment as AppointmentModel
from app.models.patient import Patient as PatientModel
from app.models.queue import Queue as QueueModel
from app.utils.dependencies import get_current_user
from app.models.user import User
import logging
import traceback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Appointment)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Создание нового приема с детальным логированием
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 НАЧАЛО СОЗДАНИЯ ПРИЕМА")
        logger.info(f"👤 Reception user: {current_user.username} (ID: {current_user.id})")
        logger.info(f"👨‍⚕️ Doctor ID: {appointment.doctor_id}")
        logger.info(f"👤 Patient ID: {appointment.patient_id}")
        logger.info(f"📅 Date: {appointment.date}")
        logger.info(f"📝 Notes: {appointment.notes}")
        logger.info(f"💰 Cost: {appointment.cost}")

        # Шаг 1: Проверка авторизации
        logger.info("🔍 Шаг 1: Проверка авторизации...")
        try:
            if current_user.role != "reception":
                logger.warning(f"⚠️ Пользователь {current_user.username} не имеет роли reception")
                raise HTTPException(status_code=403, detail="Not authorized")
            logger.info("✅ Авторизация пройдена")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке авторизации: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Authorization check error: {str(e)}")

        # Шаг 2: Проверка существования врача
        logger.info("🔍 Шаг 2: Проверка существования врача...")
        try:
            doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
            if not doctor:
                logger.warning(f"⚠️ Врач с ID {appointment.doctor_id} не найден")
                raise HTTPException(status_code=400, detail="Doctor not found")
            logger.info("✅ Врач существует")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке существования врача: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Doctor existence check error: {str(e)}")

        # Шаг 3: Проверка существования пациента
        logger.info("🔍 Шаг 3: Проверка существования пациента...")
        try:
            patient = db.query(PatientModel).filter(PatientModel.id == appointment.patient_id).first()
            if not patient:
                logger.warning(f"⚠️ Пациент с ID {appointment.patient_id} не найден")
                raise HTTPException(status_code=400, detail="Patient not found")
            logger.info("✅ Пациент существует")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке существования пациента: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Patient existence check error: {str(e)}")

        # Шаг 4: Проверка доступности врача
        logger.info("🔍 Шаг 4: Проверка доступности врача...")
        try:
            existing_appointment = db.query(AppointmentModel).filter(
                AppointmentModel.doctor_id == appointment.doctor_id,
                AppointmentModel.date == appointment.date,
            ).first()
            if existing_appointment:
                logger.warning(f"⚠️ Врач {appointment.doctor_id} занят на {appointment.date}")
                raise HTTPException(status_code=400, detail="Doctor is not available at this time")
            logger.info("✅ Врач доступен")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке доступности врача: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Doctor availability check error: {str(e)}")

        # Шаг 5: Создание объекта приема
        logger.info("📝 Шаг 5: Создание объекта приема...")
        try:
            db_appointment = AppointmentModel(**appointment.dict())
            logger.info(f"   Appointment object created: {db_appointment}")
            logger.info("✅ Объект приема создан")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании объекта приема: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Appointment object creation error: {str(e)}")

        # Шаг 6: Добавление в сессию БД
        logger.info("💾 Шаг 6: Добавление приема в БД...")
        try:
            db.add(db_appointment)
            logger.info("   Appointment added to session")
            logger.info("✅ Прием добавлен в сессию")
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении в сессию: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database session error: {str(e)}")

        # Шаг 7: Коммит в БД
        logger.info("💾 Шаг 7: Коммит изменений в БД...")
        try:
            db.commit()
            logger.info("   Commit successful")
            logger.info("✅ Изменения сохранены в БД")
        except Exception as e:
            logger.error(f"❌ Ошибка при коммите: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            db.rollback()
            logger.info("   Rollback executed")
            raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

        # Шаг 7.5: Автоматическое добавление в очередь (FIFO - в конец)
        logger.info("📋 Шаг 7.5: Добавление пациента в очередь...")
        try:
            today = date_type.today()

            # Проверяем, не находится ли пациент уже в очереди у этого врача сегодня
            existing_queue = db.query(QueueModel).filter(
                and_(
                    QueueModel.patient_id == appointment.patient_id,
                    QueueModel.doctor_id == appointment.doctor_id,
                    QueueModel.queue_date == today
                )
            ).first()

            if not existing_queue:
                # Находим максимальный номер в очереди этого врача
                max_queue = db.query(func.max(QueueModel.queue_number)).filter(
                    and_(
                        QueueModel.doctor_id == appointment.doctor_id,
                        QueueModel.queue_date == today
                    )
                ).scalar()

                # Новый пациент получает следующий номер (max + 1, или 1 если очередь пустая)
                next_queue_number = (max_queue or 0) + 1

                new_queue_entry = QueueModel(
                    patient_id=appointment.patient_id,
                    doctor_id=appointment.doctor_id,
                    queue_number=next_queue_number,
                    queue_date=today
                )
                db.add(new_queue_entry)
                db.commit()
                logger.info(f"✅ Пациент добавлен в очередь с номером {next_queue_number}")
            else:
                logger.info(f"ℹ️ Пациент уже в очереди с номером {existing_queue.queue_number}")
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении в очередь: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Не прерываем создание appointment при ошибке в очереди
            logger.warning("⚠️ Appointment создан, но очередь не обновлена")

        # Шаг 8: Обновление объекта
        logger.info("🔄 Шаг 8: Обновление объекта приема...")
        try:
            db.refresh(db_appointment)
            logger.info(f"   Appointment ID: {db_appointment.id}")
            logger.info("✅ Объект обновлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении объекта: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Не критично, продолжаем

        logger.info("=" * 80)
        logger.info("✅ СОЗДАНИЕ ПРИЕМА УСПЕШНО ЗАВЕРШЕНО")
        logger.info(f"   Appointment ID: {db_appointment.id}")
        logger.info(f"   Doctor ID: {db_appointment.doctor_id}")
        logger.info(f"   Patient ID: {db_appointment.patient_id}")
        logger.info(f"   Date: {db_appointment.date}")
        logger.info(f"   Status: {db_appointment.status}")
        logger.info("=" * 80)

        return db_appointment

    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ СОЗДАНИИ ПРИЕМА")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected appointment creation error: {str(e)}"
        )

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
    query = db.query(AppointmentModel, PatientModel.full_name.label("patient_full_name")).join(
        PatientModel, AppointmentModel.patient_id == PatientModel.id
    ).filter(AppointmentModel.doctor_id == current_user.id)
    if status:
        query = query.filter(AppointmentModel.status == status)
    results = query.all()
    appointments = []
    for appointment, patient_full_name in results:
        appointment_data = AppointmentWithDoctor(
            id=appointment.id,
            patient_full_name=patient_full_name,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment.date,
            status=appointment.status,
            notes=appointment.notes,
            cost=appointment.cost
        )
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

@router.patch("/my/{appointment_id}/cost", response_model=Appointment)
def update_appointment_cost(
    appointment_id: int,
    cost_update: AppointmentCostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update appointment cost")

    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.id == appointment_id,
        AppointmentModel.doctor_id == current_user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.cost = cost_update.cost
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/reception/done", response_model=List[AppointmentWithDoctor])
def get_done_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(AppointmentModel, PatientModel.full_name.label("patient_full_name")).join(
        PatientModel, AppointmentModel.patient_id == PatientModel.id
    ).filter(AppointmentModel.status == "done")
    results = query.all()
    appointments = []
    for appointment, patient_full_name in results:
        appointment_data = AppointmentWithDoctor(
            id=appointment.id,
            patient_full_name=patient_full_name,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment.date,
            status=appointment.status,
            notes=appointment.notes,
            cost=appointment.cost
        )
        appointments.append(appointment_data)
    return appointments

@router.patch("/reception/{appointment_id}/pay", response_model=Appointment)
def pay_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Not authorized")

    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != "done":
        raise HTTPException(status_code=400, detail="Appointment must be done before payment")

    appointment.status = "paid"
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