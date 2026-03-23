from datetime import date,timedelta
from decimal import Decimal
from celery import shared_task
from django.db.models import Count, Q
from .models import SalaryStructure
from .models import  Leave, Payroll
from teacher_app.models import  Attendance
from django.db import transaction

@shared_task
def generate_montholly_payroll(teacher_id):
    today=date.today()
    start_date=today-timedelta(days=30)
    end_date=today
    salary=SalaryStructure.objects.get(teacher_id=teacher_id)
    per_day_salary=salary.base_salary/Decimal("30")
    attendence=(
        Attendance.objects.filter(teacher_id=teacher_id,date__range=[start_date, end_date])
        .aggregate(
            present=Count("id",filter=Q(status="PRESENT")),
            half_day=Count("id",filter=Q(status="HALF_DAY"))
        )
    )
    present_days=attendence['present'] or 0
    half_days=attendence['half_day'] or 0

    leaves = Leave.objects.filter(
    teacher_id=teacher_id,
    status="APPROVED",
    start_date__lte=end_date,
    end_date__gte=start_date
)
    paid_leaves=0
    lwp_leaves=0
    for leave in leaves:
        actual_start = max(leave.start_date, start_date)
        actual_end = min(leave.end_date, end_date)
        days = (actual_end - actual_start).days + 1
        if leave.leave_type in ["CL","SICK","PAID"]:
            paid_leaves+=days
        elif leave.leave_type=="LWP":
            lwp_leaves+=days    


    gross_salary=(
        present_days*per_day_salary + (half_days * per_day_salary/2))
    net_salary=gross_salary + (paid_leaves*per_day_salary)
    print("NEW NET SALARY:", net_salary)

    with transaction.atomic():
        Payroll.objects.update_or_create(
        teacher_id=teacher_id,
        period_start=start_date,
        period_end=end_date,
        defaults={
            "present_days": present_days,
            "half_days": half_days,
            "paid_leaves": paid_leaves,
            "lwp_days": lwp_leaves,
            "gross_salary": gross_salary,
            "net_salary": net_salary
        }
    )
    return f"Payroll generated for teacher {teacher_id}"

