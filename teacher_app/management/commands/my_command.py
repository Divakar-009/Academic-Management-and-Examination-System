from django.core.management.base import BaseCommand
from django.utils import timezone
from teacher_app.models import Assignment
from teacher_app.utility import send_assignment_result_mail

class Command(BaseCommand):
    help = "Send assignment result mails to teachers"

    def handle(self, *args, **kwargs):
        assignments = Assignment.objects.filter(due_date__lt= timezone.now(),result_mail_sent=False)
        for assignment in assignments:
            send_assignment_result_mail(assignment)
            assignment.result_mail_sent = True
            assignment.save()

        self.stdout.write(self.style.SUCCESS("All assignment mails sent!"))
