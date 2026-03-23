from django.db import models
from teacher_app.models import *


# Create your models here.

class SalaryStructure(models.Model):
    teacher = models.OneToOneField(
        TecherRegist,
        on_delete=models.CASCADE,
        related_name="salary"
    )
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class PaypalAccountInfo(models.Model):
    teacher=models.OneToOneField(TecherRegist,on_delete=models.CASCADE,related_name="payment_account")
    paypalEmail=models.EmailField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=('teacher','paypalEmail')

class Leave(models.Model):
    LEAVE_TYPES=[
        ('CL','Casual Leave'),
        ('SICK','Sick Leave'),
        ('PAID','paid leave'),
        ('LWP','Leave Without Pay'),
    ]
    STATUS=[
        ('PENDING','pending'),
        ('APPROVED','Approved'),
        ('REJECTED','Rejected')
    ]
    teacher=models.ForeignKey(TecherRegist,on_delete=models.CASCADE,related_name='leave_requests')
    leave_type=models.CharField(max_length=10,choices=LEAVE_TYPES)
    start_date=models.DateField()
    end_date=models.DateField()
    reason=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS,default='PENDING')
    created_at=models.DateTimeField(auto_now_add=True)

class Payroll(models.Model):
    teacher=models.ForeignKey(TecherRegist,on_delete=models.CASCADE,related_name='payrolls')
    period_start = models.DateField()
    period_end = models.DateField()
    present_days=models.IntegerField(default=0)
    half_days=models.IntegerField(default=0)
    paid_leaves=models.IntegerField(default=0)
    lwp_days=models.IntegerField(default=0)
    gross_salary=models.DecimalField(max_digits=10,decimal_places=2)
    deductions=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    net_salary=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20,choices=[('PENDING','Pending'),('PAID','Paid')],default='PENDING')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together =["teacher","period_start","period_end"]


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("PENDING","Pending"),
        ("PROCESSING","Processing"),
        ("SUCCESS","Success"),
        ("FAILED","Failed")
    ]
    payroll=models.ForeignKey(Payroll,on_delete=models.CASCADE)
    paypal_batch_id=models.CharField(max_length=200,blank=True,null=True)
    paypal_transction_id=models.CharField(max_length=200,blank=True,unique=True,null=True)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=20,choices=PAYMENT_STATUS,default="PENDING")
    paid_at=models.DateTimeField(null=True,blank=True)
    
    
class WebHookEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

