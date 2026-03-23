from django.utils import timezone

from django.db import models
from teacher_app.models import *
from student_app.models import *

class Room(models.Model):
    teacher=models.ForeignKey(TecherRegist,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("teacher", "student")  

    def __str__(self):
        return f"{self.teacher.name} - {self.student}"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE,related_name="messages")
    sender_name=models.CharField(max_length=255)
    is_sender=models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender_name}: {self.content}"
    


    ## group chat models

class Group_Room(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(TecherRegist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class GroupMember(models.Model):
    ROLE_CHOICES = (('ADMIN', 'Admin'),('MEMBER', 'Member'),)
    USER_TYPE = (('STUDENT', 'Student'),('TEACHER', 'Teacher'),)

    group = models.ForeignKey(Group_Room, on_delete=models.CASCADE, related_name='group_members')
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TecherRegist, null=True, blank=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    user_type = models.CharField(max_length=10, choices=USER_TYPE)
    joined_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'student'],
                name='unique_student_in_group'
            ),
            models.UniqueConstraint(
                fields=['group', 'teacher'],
                name='unique_teacher_in_group'
            ),
        ]
    
class Group_message(models.Model):
    room=models.ForeignKey(Group_Room,on_delete=models.CASCADE,related_name="mssg")
    sender=models.CharField(max_length=50)
    content=models.TextField()
    is_sender=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.content}"



