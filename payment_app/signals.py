from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Attendance,Leave

@receiver(post_save,sender=Attendance)
def create_leave_from_absent(sender,instance,created,**kwargs):
    if instance.status !="ABSENT":
        return
    teacher=instance.teacher
    leave_date=instance.date
    yesterday=leave_date-timedelta(days=1)

    if leave_date.weekday() in [5,6]:
        leave_type="PAID"
    else:
        leave_type="LWP"
    leave=Leave.objects.filter(teacher=teacher,end_date=yesterday).first()
    if leave and leave.leave_type == leave_type:
        leave.end_date=leave_date
        leave.save()
    else:
        Leave.objects.create(
            teacher=teacher,
            leave_type=leave_type,
            start_date=leave_date,
            end_date=leave_date,
            reason="Auto created from Attendance",
            status="APPROVED"
        )
