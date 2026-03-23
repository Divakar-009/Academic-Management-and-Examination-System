from rest_framework import serializers
from django.contrib.auth.hashers import make_password,check_password

from teacher_app.models import *
from student_app.models import *


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=TecherRegist
        fields='__all__'
    def create(self, validated_data):
        classes = validated_data.pop('class_obj', [])
        validated_data['password'] = make_password(validated_data['password'])
        teacher = TecherRegist.objects.create(**validated_data)
        if classes:
            teacher.class_obj.set(classes)
        return teacher
    
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ('teacher', 'is_published')
   

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields='__all__'

class StudentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name']

class AssignmentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'Assignment_title']
        
class TeacherAttemptViewSerializer(serializers.ModelSerializer):
    student = StudentMiniSerializer(read_only=True)
    assignment = AssignmentMiniSerializer(read_only=True)

    class Meta:
        model = StudentAssignmentAttempt
        fields = ['id','started_at','submitted_at','is_submitted','score','student','assignment',]

class classesSerializer(serializers.ModelSerializer):
    class Meta:
        model=ClassRoom
        fields=['id','classname','section']

class StudentListSerailizer(serializers.ModelSerializer):
    class Meta:
        model=Student
        fields=['id','name','studentID']



class StudentAssignmentDetailSerializer(serializers.ModelSerializer):
    assignment_title=serializers.ReadOnlyField(source='assignment.Assignment_title')
    assignment_description=serializers.ReadOnlyField(source='assignment.description')
    percentage=serializers.SerializerMethodField()
    class Meta:
        model=StudentAssignmentAttempt
        fields=['assignment_title', 'assignment_description', 'score', 'percentage', 'submitted_at','is_submitted']

    def get_percentage(self,obj):
        try:
            total=obj.Assignment.total_marks
            return (obj.score/total)*100 if total > 0 else 0
        except AttributeError:
            return "N/A"
        
          
class StudentProfileSerializer(serializers.ModelSerializer):
    assignmets=StudentAssignmentDetailSerializer(source='studentassignmentattempt_set', many=True, read_only=True)
    total_assignment_completed=serializers.SerializerMethodField()
    class Meta:
        model=Student
        fields=[
            'id', 'studentID', 'name', 'email', 'phone', 
            'total_assignment_completed', 'assignmets'
        ]
    def get_total_assignment_completed(self,obj):
        return obj.studentassignmentattempt_set.filter(is_submitted=True).count()
    