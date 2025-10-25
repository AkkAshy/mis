from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from app.schemas.stats import (
    GeneralStats, AppointmentStats, PatientStats, DoctorStats,
    DailyStats, WeeklyStats, MonthlyStats, TimeRangeStats,
    DoctorPerformanceStats, StatsResponse, FinancialStats,
    DoctorFinancialStats, DailyFinancialStats, WeeklyFinancialStats,
    MonthlyFinancialStats, TimeRangeFinancialStats, DoctorPerformanceFinancialStats
)
from app.utils.dependencies import get_current_user

router = APIRouter()

def calculate_completion_rate(completed: int, total: int) -> float:
    """Рассчитывает процент завершенных записей"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 2)

def get_date_range(days: int) -> tuple[date, date]:
    """Возвращает диапазон дат для последних N дней"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    return start_date, end_date

@router.get("/general", response_model=GeneralStats)
def get_general_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Общая статистика системы"""
    today = date.today()
    
    # Общее количество пациентов
    total_patients = db.query(Patient).count()
    
    # Общее количество записей
    total_appointments = db.query(Appointment).count()
    
    # Общее количество врачей
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    
    # Записи на сегодня
    appointments_today = db.query(Appointment).filter(
        func.date(Appointment.date) == today
    ).count()
    
    # Завершенные записи на сегодня
    completed_today = db.query(Appointment).filter(
        func.date(Appointment.date) == today,
        Appointment.status == "done"
    ).count()
    
    # Новые пациенты сегодня
    new_patients_today = db.query(Patient).filter(
        func.date(Patient.created_at) == today
    ).count()
    
    # Общий процент завершения
    completed_total = db.query(Appointment).filter(Appointment.status == "done").count()
    completion_rate = calculate_completion_rate(completed_total, total_appointments)
    
    return GeneralStats(
        total_patients=total_patients,
        total_appointments=total_appointments,
        total_doctors=total_doctors,
        appointments_today=appointments_today,
        completed_today=completed_today,
        new_patients_today=new_patients_today,
        completion_rate=completion_rate
    )

@router.get("/appointments", response_model=AppointmentStats)
def get_appointment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика по записям"""
    total_appointments = db.query(Appointment).count()
    completed_appointments = db.query(Appointment).filter(Appointment.status == "done").count()
    pending_appointments = db.query(Appointment).filter(Appointment.status == "scheduled").count()
    completion_rate = calculate_completion_rate(completed_appointments, total_appointments)
    
    return AppointmentStats(
        total_appointments=total_appointments,
        completed_appointments=completed_appointments,
        pending_appointments=pending_appointments,
        completion_rate=completion_rate
    )

@router.get("/patients", response_model=PatientStats)
def get_patient_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика по пациентам"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_patients = db.query(Patient).count()
    new_patients_today = db.query(Patient).filter(
        func.date(Patient.created_at) == today
    ).count()
    new_patients_this_week = db.query(Patient).filter(
        func.date(Patient.created_at) >= week_ago
    ).count()
    new_patients_this_month = db.query(Patient).filter(
        func.date(Patient.created_at) >= month_ago
    ).count()
    
    return PatientStats(
        total_patients=total_patients,
        new_patients_today=new_patients_today,
        new_patients_this_week=new_patients_this_week,
        new_patients_this_month=new_patients_this_month
    )

@router.get("/doctors", response_model=List[DoctorStats])
def get_doctors_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика по врачам"""
    doctors = db.query(User).filter(User.role == "doctor").all()
    stats = []
    
    for doctor in doctors:
        total_appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor.id).count()
        completed_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "done"
        ).count()
        pending_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "scheduled"
        ).count()
        completion_rate = calculate_completion_rate(completed_appointments, total_appointments)
        
        stats.append(DoctorStats(
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            total_appointments=total_appointments,
            completed_appointments=completed_appointments,
            pending_appointments=pending_appointments,
            completion_rate=completion_rate
        ))
    
    return stats

@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="Количество дней для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ежедневная статистика за последние N дней"""
    start_date, end_date = get_date_range(days)
    
    # Получаем все даты в диапазоне
    current_date = start_date
    daily_stats = []
    
    while current_date <= end_date:
        appointments_count = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date
        ).count()
        
        completed_count = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date,
            Appointment.status == "done"
        ).count()
        
        new_patients_count = db.query(Patient).filter(
            func.date(Patient.created_at) == current_date
        ).count()
        
        daily_stats.append(DailyStats(
            date=current_date,
            appointments_count=appointments_count,
            completed_count=completed_count,
            new_patients_count=new_patients_count
        ))
        
        current_date += timedelta(days=1)
    
    return daily_stats

@router.get("/weekly", response_model=List[WeeklyStats])
def get_weekly_stats(
    weeks: int = Query(4, ge=1, le=12, description="Количество недель для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Недельная статистика"""
    today = date.today()
    weekly_stats = []
    
    for i in range(weeks):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        
        appointments_count = db.query(Appointment).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end
        ).count()
        
        completed_count = db.query(Appointment).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end,
            Appointment.status == "done"
        ).count()
        
        new_patients_count = db.query(Patient).filter(
            func.date(Patient.created_at) >= week_start,
            func.date(Patient.created_at) <= week_end
        ).count()
        
        # Детализация по дням недели
        daily_breakdown = []
        current_date = week_start
        while current_date <= week_end:
            day_appointments = db.query(Appointment).filter(
                func.date(Appointment.date) == current_date
            ).count()
            
            day_completed = db.query(Appointment).filter(
                func.date(Appointment.date) == current_date,
                Appointment.status == "done"
            ).count()
            
            day_new_patients = db.query(Patient).filter(
                func.date(Patient.created_at) == current_date
            ).count()
            
            daily_breakdown.append(DailyStats(
                date=current_date,
                appointments_count=day_appointments,
                completed_count=day_completed,
                new_patients_count=day_new_patients
            ))
            
            current_date += timedelta(days=1)
        
        weekly_stats.append(WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            appointments_count=appointments_count,
            completed_count=completed_count,
            new_patients_count=new_patients_count,
            daily_breakdown=daily_breakdown
        ))
    
    return weekly_stats

@router.get("/time-range", response_model=TimeRangeStats)
def get_time_range_stats(
    start_date: date = Query(..., description="Начальная дата"),
    end_date: date = Query(..., description="Конечная дата"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика за произвольный период"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    appointments_count = db.query(Appointment).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date
    ).count()
    
    completed_count = db.query(Appointment).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date,
        Appointment.status == "done"
    ).count()
    
    new_patients_count = db.query(Patient).filter(
        func.date(Patient.created_at) >= start_date,
        func.date(Patient.created_at) <= end_date
    ).count()
    
    completion_rate = calculate_completion_rate(completed_count, appointments_count)
    
    # Детализация по дням
    daily_breakdown = []
    current_date = start_date
    while current_date <= end_date:
        day_appointments = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date
        ).count()
        
        day_completed = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date,
            Appointment.status == "done"
        ).count()
        
        day_new_patients = db.query(Patient).filter(
            func.date(Patient.created_at) == current_date
        ).count()
        
        daily_breakdown.append(DailyStats(
            date=current_date,
            appointments_count=day_appointments,
            completed_count=day_completed,
            new_patients_count=day_new_patients
        ))
        
        current_date += timedelta(days=1)
    
    return TimeRangeStats(
        start_date=start_date,
        end_date=end_date,
        appointments_count=appointments_count,
        completed_count=completed_count,
        new_patients_count=new_patients_count,
        completion_rate=completion_rate,
        daily_breakdown=daily_breakdown
    )

@router.get("/doctor-performance", response_model=List[DoctorPerformanceStats])
def get_doctor_performance(
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика производительности врачей"""
    start_date, end_date = get_date_range(days)
    doctors = db.query(User).filter(User.role == "doctor").all()
    performance_stats = []
    
    for doctor in doctors:
        total_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).count()
        
        completed_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date,
            Appointment.status == "done"
        ).count()
        
        completion_rate = calculate_completion_rate(completed_appointments, total_appointments)
        average_per_day = round(total_appointments / days, 2) if days > 0 else 0
        
        # Находим самый продуктивный день
        daily_counts = db.query(
            func.date(Appointment.date).label('appointment_date'),
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).group_by(func.date(Appointment.date)).all()
        
        most_productive_day = None
        max_count = 0
        for day, count in daily_counts:
            if count > max_count:
                max_count = count
                most_productive_day = day.strftime('%Y-%m-%d')
        
        performance_stats.append(DoctorPerformanceStats(
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            total_appointments=total_appointments,
            completed_appointments=completed_appointments,
            completion_rate=completion_rate,
            average_appointments_per_day=average_per_day,
            most_productive_day=most_productive_day
        ))
    
    return performance_stats

@router.get("/overview", response_model=StatsResponse)
def get_stats_overview(
    start_date: Optional[date] = Query(None, description="Начальная дата для детализации"),
    end_date: Optional[date] = Query(None, description="Конечная дата для детализации"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Общий обзор статистики"""
    # Получаем общую статистику
    general_stats = get_general_stats(db, current_user)
    appointment_stats = get_appointment_stats(db, current_user)
    patient_stats = get_patient_stats(db, current_user)
    doctor_stats = get_doctors_stats(db, current_user)
    
    # Если указан диапазон дат, добавляем детализацию
    time_range_stats = None
    if start_date and end_date:
        time_range_stats = get_time_range_stats(start_date, end_date, db, current_user)
    
    return StatsResponse(
        general=general_stats,
        appointments=appointment_stats,
        patients=patient_stats,
        doctors=doctor_stats,
        time_range=time_range_stats
    )

# Финансовые эндпоинты

@router.get("/financial", response_model=FinancialStats)
def get_financial_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Общая финансовая статистика"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Общая выручка
    total_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).scalar()
    
    # Выручка от завершенных записей
    completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        Appointment.status == "done"
    ).scalar()
    
    # Выручка от ожидающих записей
    pending_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        Appointment.status == "scheduled"
    ).scalar()
    
    # Средняя стоимость приема
    avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).scalar()
    
    # Выручка сегодня
    revenue_today = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) == today
    ).scalar()
    
    # Выручка за неделю
    revenue_this_week = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= week_ago
    ).scalar()
    
    # Выручка за месяц
    revenue_this_month = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= month_ago
    ).scalar()
    
    return FinancialStats(
        total_revenue=total_revenue,
        completed_revenue=completed_revenue,
        pending_revenue=pending_revenue,
        average_appointment_cost=avg_cost,
        revenue_today=revenue_today,
        revenue_this_week=revenue_this_week,
        revenue_this_month=revenue_this_month
    )

@router.get("/financial/doctors", response_model=List[DoctorFinancialStats])
def get_doctors_financial_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Финансовая статистика по врачам"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    doctors = db.query(User).filter(User.role == "doctor").all()
    stats = []
    
    for doctor in doctors:
        # Общая выручка врача
        total_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id
        ).scalar()
        
        # Выручка от завершенных записей
        completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "done"
        ).scalar()
        
        # Выручка от ожидающих записей
        pending_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "scheduled"
        ).scalar()
        
        # Средняя стоимость приема
        avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id
        ).scalar()
        
        # Количество записей
        appointments_count = db.query(Appointment).filter(Appointment.doctor_id == doctor.id).count()
        
        # Выручка сегодня
        revenue_today = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) == today
        ).scalar()
        
        # Выручка за неделю
        revenue_this_week = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= week_ago
        ).scalar()
        
        # Выручка за месяц
        revenue_this_month = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= month_ago
        ).scalar()
        
        stats.append(DoctorFinancialStats(
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            total_revenue=total_revenue,
            completed_revenue=completed_revenue,
            pending_revenue=pending_revenue,
            average_appointment_cost=avg_cost,
            appointments_count=appointments_count,
            revenue_today=revenue_today,
            revenue_this_week=revenue_this_week,
            revenue_this_month=revenue_this_month
        ))
    
    return stats

@router.get("/financial/daily", response_model=List[DailyFinancialStats])
def get_daily_financial_stats(
    days: int = Query(7, ge=1, le=30, description="Количество дней для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ежедневная финансовая статистика"""
    start_date, end_date = get_date_range(days)
    
    current_date = start_date
    daily_stats = []
    
    while current_date <= end_date:
        # Общая выручка за день
        revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date
        ).scalar()
        
        # Выручка от завершенных записей
        completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date,
            Appointment.status == "done"
        ).scalar()
        
        # Количество записей
        appointments_count = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date
        ).count()
        
        # Средняя стоимость
        avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date
        ).scalar()
        
        daily_stats.append(DailyFinancialStats(
            date=current_date,
            revenue=revenue,
            completed_revenue=completed_revenue,
            appointments_count=appointments_count,
            average_cost=avg_cost
        ))
        
        current_date += timedelta(days=1)
    
    return daily_stats

@router.get("/financial/weekly", response_model=List[WeeklyFinancialStats])
def get_weekly_financial_stats(
    weeks: int = Query(4, ge=1, le=12, description="Количество недель для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Недельная финансовая статистика"""
    today = date.today()
    weekly_stats = []
    
    for i in range(weeks):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        
        # Общая выручка за неделю
        total_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end
        ).scalar()
        
        # Выручка от завершенных записей
        completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end,
            Appointment.status == "done"
        ).scalar()
        
        # Количество записей
        appointments_count = db.query(Appointment).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end
        ).count()
        
        # Средняя стоимость
        avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
            func.date(Appointment.date) >= week_start,
            func.date(Appointment.date) <= week_end
        ).scalar()
        
        # Детализация по дням недели
        daily_breakdown = []
        current_date = week_start
        while current_date <= week_end:
            day_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
                func.date(Appointment.date) == current_date
            ).scalar()
            
            day_completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
                func.date(Appointment.date) == current_date,
                Appointment.status == "done"
            ).scalar()
            
            day_appointments = db.query(Appointment).filter(
                func.date(Appointment.date) == current_date
            ).count()
            
            day_avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
                func.date(Appointment.date) == current_date
            ).scalar()
            
            daily_breakdown.append(DailyFinancialStats(
                date=current_date,
                revenue=day_revenue,
                completed_revenue=day_completed_revenue,
                appointments_count=day_appointments,
                average_cost=day_avg_cost
            ))
            
            current_date += timedelta(days=1)
        
        weekly_stats.append(WeeklyFinancialStats(
            week_start=week_start,
            week_end=week_end,
            total_revenue=total_revenue,
            completed_revenue=completed_revenue,
            appointments_count=appointments_count,
            average_cost=avg_cost,
            daily_breakdown=daily_breakdown
        ))
    
    return weekly_stats

@router.get("/financial/time-range", response_model=TimeRangeFinancialStats)
def get_time_range_financial_stats(
    start_date: date = Query(..., description="Начальная дата"),
    end_date: date = Query(..., description="Конечная дата"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Финансовая статистика за произвольный период"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Общая выручка за период
    total_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date
    ).scalar()
    
    # Выручка от завершенных записей
    completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date,
        Appointment.status == "done"
    ).scalar()
    
    # Выручка от ожидающих записей
    pending_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date,
        Appointment.status == "scheduled"
    ).scalar()
    
    # Количество записей
    appointments_count = db.query(Appointment).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date
    ).count()
    
    # Средняя стоимость
    avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
        func.date(Appointment.date) >= start_date,
        func.date(Appointment.date) <= end_date
    ).scalar()
    
    # Детализация по дням
    daily_breakdown = []
    current_date = start_date
    while current_date <= end_date:
        day_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date
        ).scalar()
        
        day_completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date,
            Appointment.status == "done"
        ).scalar()
        
        day_appointments = db.query(Appointment).filter(
            func.date(Appointment.date) == current_date
        ).count()
        
        day_avg_cost = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
            func.date(Appointment.date) == current_date
        ).scalar()
        
        daily_breakdown.append(DailyFinancialStats(
            date=current_date,
            revenue=day_revenue,
            completed_revenue=day_completed_revenue,
            appointments_count=day_appointments,
            average_cost=day_avg_cost
        ))
        
        current_date += timedelta(days=1)
    
    return TimeRangeFinancialStats(
        start_date=start_date,
        end_date=end_date,
        total_revenue=total_revenue,
        completed_revenue=completed_revenue,
        pending_revenue=pending_revenue,
        appointments_count=appointments_count,
        average_cost=avg_cost,
        daily_breakdown=daily_breakdown
    )

@router.get("/financial/doctor-performance", response_model=List[DoctorPerformanceFinancialStats])
def get_doctor_performance_financial(
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Финансовая производительность врачей"""
    start_date, end_date = get_date_range(days)
    doctors = db.query(User).filter(User.role == "doctor").all()
    performance_stats = []
    
    for doctor in doctors:
        # Общая выручка врача за период
        total_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).scalar()
        
        # Выручка от завершенных записей
        completed_revenue = db.query(func.coalesce(func.sum(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date,
            Appointment.status == "done"
        ).scalar()
        
        # Количество записей
        appointments_count = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).count()
        
        # Средняя стоимость приема
        avg_appointment_value = db.query(func.coalesce(func.avg(Appointment.cost), 0)).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).scalar()
        
        # Средняя дневная выручка
        average_daily_revenue = round(float(total_revenue) / days, 2) if days > 0 else 0
        
        # Самый прибыльный день
        daily_revenue = db.query(
            func.date(Appointment.date).label('appointment_date'),
            func.coalesce(func.sum(Appointment.cost), 0).label('revenue')
        ).filter(
            Appointment.doctor_id == doctor.id,
            func.date(Appointment.date) >= start_date,
            func.date(Appointment.date) <= end_date
        ).group_by(func.date(Appointment.date)).all()
        
        most_profitable_day = None
        most_profitable_day_revenue = None
        max_revenue = 0
        for day, revenue in daily_revenue:
            if revenue > max_revenue:
                max_revenue = revenue
                most_profitable_day = day.strftime('%Y-%m-%d')
                most_profitable_day_revenue = revenue
        
        performance_stats.append(DoctorPerformanceFinancialStats(
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            total_revenue=total_revenue,
            completed_revenue=completed_revenue,
            average_daily_revenue=average_daily_revenue,
            most_profitable_day=most_profitable_day,
            most_profitable_day_revenue=most_profitable_day_revenue,
            appointments_count=appointments_count,
            average_appointment_value=avg_appointment_value
        ))
    
    return performance_stats
