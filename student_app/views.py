from urllib import request
from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from core import settings
from student_app.permissions import IsStudent
from .models import *
from .serializers import *
from core.authentication import encode
from django.core.mail import send_mail

# Create your views here.

class StudentRegisterView(viewsets.ModelViewSet):
    queryset=Student.objects.all()
    serializer_class=StudentSerializer

class StudentLoginView(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        user=Student.objects.filter(email=email).first()
        if not user:
            return Response(
                {"message":"Invalid Credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not check_password(password,user.password):
            return Response(
                {"message":"Invalid Password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        token=encode(user)
        return Response({
            'access_token':token['access'],
            'refresh_token':token['refresh']
        },
        status=status.HTTP_200_OK
     )
    
class StudentViewAssignmentListsApi(APIView):
    permission_classes=[IsStudent]
    def get(self):
        student=self.request.user
        assignmets=Assignment.objects.filter(class_obj=student.class_obj,is_published=True)
        serializer = StudentAssignmentListSerializer(assignmets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentAssignmentApiview(APIView):
    permission_classes=[IsStudent]

    def get(self,request,assignment_id):
        try:
            assignment=Assignment.objects.get(id=assignment_id,is_published=True,class_obj=request.user.class_obj)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )   
        serializer=StudentAssignmentDetailSerializer(assignment)
        return Response(serializer.data)

class submitAssignmentAPIView(APIView):
    permission_classes=[IsStudent]
    def post(self,request,assignment_id):
        try:
            assignment=Assignment.objects.get(id=assignment_id,is_published=True,class_obj=request.user.class_obj)
        except Assignment.DoesNotExist:
            return Response(
                {"error":"Assignment not Found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if assignment.due_date<=timezone.now():
            return Response({
                "message":"Submission time is over"
            },status=status.HTTP_400_BAD_REQUEST)
        
        if StudentAssignmentAttempt.objects.filter(student=request.user,assignment=assignment,is_submitted=True).exists():
            return Response(
                {"error": "Already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attempt = StudentAssignmentAttempt.objects.create(student=request.user,assignment=assignment)

        score = 0
        for ans in request.data['answers']:
            try:
                question=Question.objects.get(id=ans['question_id'])
            except Question.DoesNotExist:
                return Response({
                    "message":"Invalid Question"
                },status=status.HTTP_400_BAD_REQUEST)
            StudentAnswer.objects.create(attempt=attempt,question=question,selected_option=ans['selected_option'])
            if ans['selected_option']==question.correct_option:
                score+=question.marks
        attempt.score = score
        attempt.is_submitted=True
        attempt.submitted_at=timezone.now()
        attempt.save()
        return Response({
            'message':"submitted",
            "score":attempt.score 
        })
