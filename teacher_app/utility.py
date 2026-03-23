from django.core.mail import send_mail
from student_app.models import *
from django.db.models import Count,Q

def send_assignment_result_mail(assignment):
    students = Student.objects.filter(class_obj=assignment.class_obj)
    total_students = students.count()

    attempts = (StudentAssignmentAttempt.objects.filter(assignment=assignment, is_submitted=True).select_related("student"))
    stats=attempts.aggregate(
    total_attempts = Count("id"),
    passed_count =Count("id",filter=Q(score__gte=5)),
    failed_count = Count("id",filter=Q(score__lt=5)),
    )
    

    passed_details = ",".join([f"{a.student.name} ({a.score})" for a in attempts if a.score>=5])
    failed_details = ",".join([f"{a.student.name} ({a.score})" for a in attempts if a.score<5])

    message = f"""
Assignment name: {assignment.Assignment_title}
Class: {assignment.class_obj.classname}
Total Students: {total_students}
Total Attempts: {stats['total_attempts']}
Passed ({stats['passed_count']}): {passed_details}
Failed ({stats['failed_count']}): {failed_details}
"""

    print(f"Sending assignment result mail to: {assignment.teacher.email}")
    
    send_mail(
        subject=f"Assignment Result - {assignment.Assignment_title}",
        message=message,
        from_email='divakarsharma092003@gmail.com',
        # recipient_list=[assignment.teacher.email],
        recipient_list=['divakarsharma092003@gmail.com'],
        fail_silently=False
    )
