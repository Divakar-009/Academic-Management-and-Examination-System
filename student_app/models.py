from django.db import models
from teacher_app.models import *
# Create your models here.


class Student(models.Model):
    name=models.CharField(max_length=30)
    class_obj=models.ForeignKey(ClassRoom,on_delete=models.CASCADE,related_name="SclassObj")
    phone=models.CharField(max_length=11)
    dob=models.DateField()
    studentID=models.CharField(max_length=50,blank=True,unique=True)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=200,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class StudentAssignmentAttempt(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    assignment=models.ForeignKey(Assignment,on_delete=models.CASCADE)
    started_at=models.DateTimeField(auto_now_add=True)
    submitted_at=models.DateTimeField(null=True,blank=True)
    is_submitted=models.BooleanField(default=False)
    score=models.IntegerField(default=0)
    def __str__(self):
        return f"{self.student.name} - {self.assignment.Assignment_title}"

class StudentAnswer(models.Model):
    attempt=models.ForeignKey(StudentAssignmentAttempt,related_name='answers', on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'),(2, 'Option 2'),(3, 'Option 3'),(4, 'Option 4'),],
        null=True,blank=True)
    



    

