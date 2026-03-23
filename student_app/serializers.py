from rest_framework import serializers
from django.contrib.auth.hashers import make_password,check_password

from .models import *
from teacher_app.models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Student
        fields=['id','name','class_obj','dob','phone','studentID','email','password']
        read_only=['name','class_obj','dob','phone','studentID','email']

    def create(self, validated_data):
        validated_data['password']=make_password(validated_data['password'])
        return Student.objects.create(**validated_data)
    
class StudentAssignmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'Assignment_title']


class StudentQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()  

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']

    def get_options(self, obj):
        return {
            "1": obj.option1,
            "2": obj.option2,
            "3": obj.option3,
            "4": obj.option4,
        }
class StudentAssignmentDetailSerializer(serializers.ModelSerializer):
    questions= StudentQuestionSerializer(many=True)
    class Meta:
        model = Assignment
        fields = [
            'id',
            'Assignment_title',
            'description',
            'due_date',
            'questions',
            'total_marks'
        ]