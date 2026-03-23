from django.db import models

# Create your models here.


class ClassRoom(models.Model):
    classname=models.CharField(max_length=50)
    section=models.CharField(max_length=10,blank=True)

    def __str__(self):
        return self.classname


class TecherRegist(models.Model):
    name=models.CharField(max_length=20)
    phone=models.CharField(max_length=11)
    dob=models.DateField()
    class_obj=models.ManyToManyField(ClassRoom,related_name="classObj")
    department=models.CharField(max_length=50)
    employeeID=models.CharField(max_length=50,blank=True,unique=True)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=200,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    STATUS_CHOICES=[
        ('PRESENT','Present'),
        ('HALF_DAY','Half Day'),
        ('ABSENT','Absent'),
    ]
    teacher=models.ForeignKey(TecherRegist,on_delete=models.CASCADE,related_name="attendance_records")
    date=models.DateField()
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="ABSENT")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=['teacher','date']


class Assignment(models.Model):
    teacher=models.ForeignKey(TecherRegist,on_delete=models.CASCADE)
    class_obj=models.ForeignKey(ClassRoom,on_delete=models.CASCADE)
    Assignment_title=models.CharField(max_length=50)
    description=models.TextField()
    is_published = models.BooleanField(default=False)
    due_date=models.DateTimeField()
    total_marks=models.CharField(max_length=20)
    result_mail_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return self.Assignment_title

class Question(models.Model):
    assignment=models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='questions')
    question_text=models.TextField()
    option1 = models.CharField(max_length=200,null=True)
    option2 = models.CharField(max_length=200,null=True)
    option3 = models.CharField(max_length=200,null=True)
    option4 = models.CharField(max_length=200,null=True)

    correct_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'),(2, 'Option 2'),(3, 'Option 3'),(4, 'Option 4'),],
        null=True,blank=True)
    marks=models.PositiveIntegerField(null=True,blank=True)
    def __str__(self):
        return self.question_text
    
class BlacklistedRefreshToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


