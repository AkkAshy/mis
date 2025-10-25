from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal

class AppointmentStats(BaseModel):
    total_appointments: int
    completed_appointments: int
    pending_appointments: int
    completion_rate: float

class PatientStats(BaseModel):
    total_patients: int
    new_patients_today: int
    new_patients_this_week: int
    new_patients_this_month: int

class DoctorStats(BaseModel):
    doctor_id: int
    doctor_name: str
    total_appointments: int
    completed_appointments: int
    pending_appointments: int
    completion_rate: float

class DailyStats(BaseModel):
    date: date
    appointments_count: int
    completed_count: int
    new_patients_count: int

class WeeklyStats(BaseModel):
    week_start: date
    week_end: date
    appointments_count: int
    completed_count: int
    new_patients_count: int
    daily_breakdown: List[DailyStats]

class MonthlyStats(BaseModel):
    month: int
    year: int
    appointments_count: int
    completed_count: int
    new_patients_count: int
    weekly_breakdown: List[WeeklyStats]

class GeneralStats(BaseModel):
    total_patients: int
    total_appointments: int
    total_doctors: int
    appointments_today: int
    completed_today: int
    new_patients_today: int
    completion_rate: float

class TimeRangeStats(BaseModel):
    start_date: date
    end_date: date
    appointments_count: int
    completed_count: int
    new_patients_count: int
    completion_rate: float
    daily_breakdown: List[DailyStats]

class DoctorPerformanceStats(BaseModel):
    doctor_id: int
    doctor_name: str
    total_appointments: int
    completed_appointments: int
    completion_rate: float
    average_appointments_per_day: float
    most_productive_day: Optional[str] = None

# Финансовые схемы
class FinancialStats(BaseModel):
    total_revenue: Decimal
    completed_revenue: Decimal
    pending_revenue: Decimal
    average_appointment_cost: Decimal
    revenue_today: Decimal
    revenue_this_week: Decimal
    revenue_this_month: Decimal

class DoctorFinancialStats(BaseModel):
    doctor_id: int
    doctor_name: str
    total_revenue: Decimal
    completed_revenue: Decimal
    pending_revenue: Decimal
    average_appointment_cost: Decimal
    appointments_count: int
    revenue_today: Decimal
    revenue_this_week: Decimal
    revenue_this_month: Decimal

class DailyFinancialStats(BaseModel):
    date: date
    revenue: Decimal
    completed_revenue: Decimal
    appointments_count: int
    average_cost: Decimal

class WeeklyFinancialStats(BaseModel):
    week_start: date
    week_end: date
    total_revenue: Decimal
    completed_revenue: Decimal
    appointments_count: int
    average_cost: Decimal
    daily_breakdown: List[DailyFinancialStats]

class MonthlyFinancialStats(BaseModel):
    month: int
    year: int
    total_revenue: Decimal
    completed_revenue: Decimal
    appointments_count: int
    average_cost: Decimal
    weekly_breakdown: List[WeeklyFinancialStats]

class TimeRangeFinancialStats(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal
    completed_revenue: Decimal
    pending_revenue: Decimal
    appointments_count: int
    average_cost: Decimal
    daily_breakdown: List[DailyFinancialStats]

class DoctorPerformanceFinancialStats(BaseModel):
    doctor_id: int
    doctor_name: str
    total_revenue: Decimal
    completed_revenue: Decimal
    average_daily_revenue: Decimal
    most_profitable_day: Optional[str] = None
    most_profitable_day_revenue: Optional[Decimal] = None
    appointments_count: int
    average_appointment_value: Decimal

class StatsResponse(BaseModel):
    general: GeneralStats
    appointments: AppointmentStats
    patients: PatientStats
    doctors: List[DoctorStats]
    financial: Optional[FinancialStats] = None
    time_range: Optional[TimeRangeStats] = None
