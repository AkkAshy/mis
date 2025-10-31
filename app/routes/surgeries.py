from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.surgery import SurgeryCreate, Surgery, SurgeryUpdate, SurgeryWithDetails
from app.models.surgery import Surgery as SurgeryModel
from app.models.patient import Patient as PatientModel
from app.models.user import User
from app.utils.dependencies import get_current_user
import logging
import traceback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Surgery)
def create_surgery(
    surgery: SurgeryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание новой операции (только врач может создавать)
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 НАЧАЛО СОЗДАНИЯ ОПЕРАЦИИ")
        logger.info(f"👤 Doctor user: {current_user.username} (ID: {current_user.id})")
        logger.info(f"👤 Patient ID: {surgery.patient_id}")
        logger.info(f"👨‍⚕️ Surgeon ID: {surgery.surgeon_id}")
        logger.info(f"🔪 Operation: {surgery.operation_name}")
        logger.info(f"📅 Date: {surgery.operation_date}")

        # Шаг 1: Проверка авторизации (только врач)
        logger.info("🔍 Шаг 1: Проверка авторизации...")
        if current_user.role != "doctor":
            logger.warning(f"⚠️ Пользователь {current_user.username} не имеет роли doctor")
            raise HTTPException(status_code=403, detail="Only doctors can create surgeries")
        logger.info("✅ Авторизация пройдена")

        # Шаг 2: Проверка существования пациента
        logger.info("🔍 Шаг 2: Проверка существования пациента...")
        patient = db.query(PatientModel).filter(PatientModel.id == surgery.patient_id).first()
        if not patient:
            logger.warning(f"⚠️ Пациент с ID {surgery.patient_id} не найден")
            raise HTTPException(status_code=400, detail="Patient not found")
        logger.info("✅ Пациент существует")

        # Шаг 3: Проверка существования хирурга
        logger.info("🔍 Шаг 3: Проверка существования хирурга...")
        surgeon = db.query(User).filter(User.id == surgery.surgeon_id, User.role == "doctor").first()
        if not surgeon:
            logger.warning(f"⚠️ Хирург с ID {surgery.surgeon_id} не найден")
            raise HTTPException(status_code=400, detail="Surgeon not found")
        logger.info("✅ Хирург существует")

        # Шаг 4: Создание объекта операции
        logger.info("📝 Шаг 4: Создание объекта операции...")
        surgery_data = surgery.dict()
        surgery_data["created_by"] = current_user.id
        db_surgery = SurgeryModel(**surgery_data)
        logger.info("✅ Объект операции создан")

        # Шаг 5: Добавление в сессию БД
        logger.info("💾 Шаг 5: Добавление операции в БД...")
        db.add(db_surgery)
        db.commit()
        db.refresh(db_surgery)
        logger.info(f"✅ Операция создана с ID: {db_surgery.id}")

        logger.info("=" * 80)
        logger.info("✅ СОЗДАНИЕ ОПЕРАЦИИ УСПЕШНО ЗАВЕРШЕНО")
        logger.info("=" * 80)

        return db_surgery

    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ СОЗДАНИИ ОПЕРАЦИИ")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=List[SurgeryWithDetails])
def get_surgeries(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    surgeon_id: Optional[int] = Query(None, description="Filter by surgeon ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка операций (врачи видят свои операции, reception все)
    """
    if current_user.role not in ["doctor", "reception"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(
        SurgeryModel,
        PatientModel.full_name.label("patient_full_name"),
        User.full_name.label("surgeon_full_name")
    ).join(
        PatientModel, SurgeryModel.patient_id == PatientModel.id
    ).join(
        User, SurgeryModel.surgeon_id == User.id
    )

    # Фильтры
    if patient_id:
        query = query.filter(SurgeryModel.patient_id == patient_id)
    if surgeon_id:
        query = query.filter(SurgeryModel.surgeon_id == surgeon_id)

    # Врачи видят только свои операции
    if current_user.role == "doctor":
        query = query.filter(SurgeryModel.surgeon_id == current_user.id)

    results = query.offset(skip).limit(limit).all()

    surgeries = []
    for surgery, patient_full_name, surgeon_full_name in results:
        surgery_data = SurgeryWithDetails(
            id=surgery.id,
            patient_id=surgery.patient_id,
            patient_full_name=patient_full_name,
            surgeon_id=surgery.surgeon_id,
            surgeon_full_name=surgeon_full_name,
            operation_name=surgery.operation_name,
            operation_date=surgery.operation_date,
            start_time=surgery.start_time,
            end_time=surgery.end_time,
            pre_op_days=surgery.pre_op_days,
            post_op_days=surgery.post_op_days,
            notes=surgery.notes,
            complications=surgery.complications,
            outcome=surgery.outcome,
            additional_data=surgery.additional_data,
            created_by=surgery.created_by,
            created_at=surgery.created_at,
            updated_at=surgery.updated_at
        )
        surgeries.append(surgery_data)

    return surgeries

@router.get("/{surgery_id}", response_model=SurgeryWithDetails)
def get_surgery(
    surgery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение деталей операции
    """
    if current_user.role not in ["doctor", "reception"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = db.query(
        SurgeryModel,
        PatientModel.full_name.label("patient_full_name"),
        User.full_name.label("surgeon_full_name")
    ).join(
        PatientModel, SurgeryModel.patient_id == PatientModel.id
    ).join(
        User, SurgeryModel.surgeon_id == User.id
    ).filter(SurgeryModel.id == surgery_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Surgery not found")

    surgery, patient_full_name, surgeon_full_name = result

    # Врачи могут видеть только свои операции
    if current_user.role == "doctor" and surgery.surgeon_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this surgery")

    return SurgeryWithDetails(
        id=surgery.id,
        patient_id=surgery.patient_id,
        patient_full_name=patient_full_name,
        surgeon_id=surgery.surgeon_id,
        surgeon_full_name=surgeon_full_name,
        operation_name=surgery.operation_name,
        operation_date=surgery.operation_date,
        start_time=surgery.start_time,
        end_time=surgery.end_time,
        pre_op_days=surgery.pre_op_days,
        post_op_days=surgery.post_op_days,
        notes=surgery.notes,
        complications=surgery.complications,
        outcome=surgery.outcome,
        additional_data=surgery.additional_data,
        created_by=surgery.created_by,
        created_at=surgery.created_at,
        updated_at=surgery.updated_at
    )

@router.patch("/{surgery_id}", response_model=Surgery)
def update_surgery(
    surgery_id: int,
    surgery_update: SurgeryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление операции (только хирург операции или reception)
    """
    if current_user.role not in ["doctor", "reception"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    surgery = db.query(SurgeryModel).filter(SurgeryModel.id == surgery_id).first()
    if not surgery:
        raise HTTPException(status_code=404, detail="Surgery not found")

    # Врачи могут обновлять только свои операции
    if current_user.role == "doctor" and surgery.surgeon_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this surgery")

    update_data = surgery_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(surgery, field, value)

    db.commit()
    db.refresh(surgery)
    return surgery

@router.delete("/{surgery_id}")
def delete_surgery(
    surgery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление операции (только reception)
    """
    if current_user.role != "reception":
        raise HTTPException(status_code=403, detail="Only reception can delete surgeries")

    surgery = db.query(SurgeryModel).filter(SurgeryModel.id == surgery_id).first()
    if not surgery:
        raise HTTPException(status_code=404, detail="Surgery not found")

    db.delete(surgery)
    db.commit()
    return {"message": "Surgery deleted successfully"}