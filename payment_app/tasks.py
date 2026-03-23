from celery import shared_task
from django.conf import settings
from payment_app.models import Payment, Payroll
from payment_app.paypal_service import check_payout_status, get_paypal_access_token, send_salary
from payment_app.payroll_service import generate_montholly_payroll
from teacher_app.models import TecherRegist
from django.core.mail import send_mail

@shared_task
def generate_payroll_forTeacher():
    teacher_ids=TecherRegist.objects.values_list("id",flat=True)
    for teacher_id in teacher_ids:
        generate_montholly_payroll.delay(teacher_id)
    return "payroll jobs scheduled"

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries":5})
def process_salary_payment(self,payment_id):
    payment = Payment.objects.get(id=payment_id)
    try:
        payment.status="PROCESSING"
        payment.save()
        send_salary(payment)
        confirm_paypal_payment.delay(payment.id)
    except Exception as e:
        payment.status="FAILED"
        payment.save()
        raise self.retry(exc=e,countdown=60)
    


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries":3})
def send_salary_receipt_email(self,teacher_id,payroll_id):
    teacher = TecherRegist.objects.get(id=teacher_id)
    payroll = Payroll.objects.get(id=payroll_id)
    subject="Salary Payment Reciept"
    message=f"""
Hello {teacher.name},

Your salary has been successfully credited.

          Salary Details
----------------------------------

Payroll Period : {payroll.period_start} to {payroll.period_end}

Present Days   : {payroll.present_days}
Half Days      : {payroll.half_days}
Paid Leaves    : {payroll.paid_leaves}
LWP Days       : {payroll.lwp_days}

Gross Salary   : {payroll.gross_salary}
Deductions     : {payroll.deductions}
Net Salary     : {payroll.net_salary}

Payment Status : {payroll.status}

Thank you.
HR
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [teacher.email],
        fail_silently=False,

    )


@shared_task(bind=True,max_retries=5)
def confirm_paypal_payment(self,payment_id):
    try:
        payment=Payment.objects.get(id=payment_id)
        if not payment.paypal_batch_id:
            return
        access_token = get_paypal_access_token() 
        status = check_payout_status(payment.paypal_batch_id, access_token)
        if status == "SUCCESS":
            payment.status = "SUCCESS"
        elif status == "PENDING":
            payment.status = "PROCESSING"
        else:
            payment.status = "FAILED"
        payment.save()
    except Payment.DoesNotExist:
        pass
    except Exception as e:
        self.retry(exc=e, countdown=60)