from tokenize import TokenError
from urllib import request
from django.shortcuts import render
import jwt
from django.shortcuts import get_object_or_404
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from core import settings
from teacher_app.permisions import IsJWTAuthorized
from teacher_app.tasks import publish_send_mail, send_assignment_results
from .models import *
from student_app.models import Student
from .serializers import *
from core.authentication import encode
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class TeacherRegisterView(viewsets.ModelViewSet):
    queryset=TecherRegist.objects.all()
    serializer_class=TeacherSerializer

class TeacherLoginView(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        user=TecherRegist.objects.filter(email=email).first()
        if not user:
            return Response(
                    {'message':"Invalid Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
            ) 
        elif not check_password(password,user.password):
            return Response(
                {'message':'Invalid Password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token=encode(user)
        return Response({
            'access_token':token['access'],
            'refresh_token':token['refresh']
        },
        status=status.HTTP_200_OK
     )

class LogoutApiView(APIView):
    permission_classes=[IsJWTAuthorized]

    def post(self,request):
        refresh_token=request.data.get('refresh_token')
        if not refresh_token:
            return Response({"message": "Token required"}, status=400)
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            BlacklistedRefreshToken.objects.create(
                jti=payload["jti"]
            ) 
            return Response({"detail": "Logout successful"})

        except jwt.ExpiredSignatureError:
            return Response({"message": "Token expired"}, status=400)

        except jwt.InvalidTokenError:
            return Response({"message": "Invalid token"}, status=400)
        
    
class AssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsJWTAuthorized]
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsJWTAuthorized]
    queryset=Question.objects.all()
    serializer_class=QuestionSerializer
    def create(self, request, *args, **kwargs):
        assignment_id=request.data.get('assignment')
        correct_option=request.data.get('correct_option')

        try:
            assignment=Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {'error':'assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if assignment.is_published:
            return Response(
                {"error":"cannot add question to published assignment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if correct_option not in [1,2,3,4]:
            return Response({"error": "correct_option must be between 1 and 4"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class AssignPublishAPIView(APIView):
    permission_classes=[IsJWTAuthorized]
    def patch(self,request,assignment_id):
        try:
            assignment=Assignment.objects.get(id=assignment_id,teacher=request.user)
        except Assignment.DoesNotExist:
            return Response(
            {"error": "Assignment not found"},
            status=status.HTTP_404_NOT_FOUND
            )
        if assignment.is_published:
            return Response(
                {"message": "Assignment already published"},
                status=status.HTTP_400_BAD_REQUEST

            )
        if assignment.due_date <= timezone.now():
            return Response({
                "message": "Cannot publish assignment. Due date already passed."},
                status=status.HTTP_400_BAD_REQUEST)

        assignment.is_published=True
        assignment.save()

        send_assignment_results.apply_async(
            args=[assignment_id],
            eta=assignment.due_date
        )

        
        emails=list(Student.objects.filter(class_obj=assignment.class_obj).values_list('email',flat=True))
        if emails:
            publish_send_mail.delay(
                emails,
                assignment.Assignment_title,
                assignment.description,
                assignment.due_date
            )

        return Response(
            {"message": "Assignment published successfully"},
            status=status.HTTP_200_OK
        )
    
class AssignmentAttemptViewset(viewsets.ModelViewSet):
    http_method_names=['get']
    permission_classes=[IsJWTAuthorized]
    queryset=StudentAssignmentAttempt.objects.all()
    serializer_class=TeacherAttemptViewSerializer


class ClassesGetByTeacher(viewsets.ModelViewSet):
    http_method_names=['get']
    permission_classes=[IsJWTAuthorized]
    serializer_class=classesSerializer
    def get_queryset(self):
        teacher=self.request.user
        return teacher.class_obj.all()

class StudentListViewSet(APIView):
    permission_classes=[IsJWTAuthorized]
    serializer_class=StudentListSerailizer
    def get(self,request,class_obj):
        class_inst=get_object_or_404(ClassRoom,id=class_obj)
        student=Student.objects.filter(class_obj=class_obj)
        if not student.exists():
            return Response({"message":"no Student in class"},status=status.HTTP_400_BAD_REQUEST)
        serializer=StudentListSerailizer(student,many=True)
        return Response(serializer.data)
    
class StudentProfileViewset(APIView):
    permission_classes=[IsJWTAuthorized]
    def get(self,request,student_id):
        student=get_object_or_404(Student,id=student_id)
        serializer=StudentProfileSerializer(student)
        return Response(serializer.data)
        

            
        
        
    









   



