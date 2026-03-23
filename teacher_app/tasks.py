from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from student_app.models import Assignment
from .utility import send_assignment_result_mail

@shared_task
def send_assignment_results(assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    send_assignment_result_mail(assignment)
    assignment.result_mail_sent = True
    assignment.save()

@shared_task
def publish_send_mail(emails, title, description, due_date):
    send_mail(
        subject="New Assignment has come",
        message=f"""
New Assignment: {title}
{description}
Last Date of submission: {due_date}
Please login and attempt the assignment.
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False
    )
   