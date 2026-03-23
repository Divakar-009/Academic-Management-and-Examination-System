from django.urls import include, path
from rest_framework import routers

from teacher_app.views import *



router=routers.DefaultRouter()
router.register(r'teachRegist',TeacherRegisterView)
router.register(r'assignment',AssignmentViewSet)
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'ExamAttemptView', AssignmentAttemptViewset)
router.register(r'getClasses', ClassesGetByTeacher,basename='getclasses')


urlpatterns =router.urls+[
    path('teacherLog/',TeacherLoginView.as_view()),
    path('assignments/<int:assignment_id>/publish/',AssignPublishAPIView.as_view()),
    path("Teacherlogout/", LogoutApiView.as_view()),
    path("getStudent/<int:class_obj>/", StudentListViewSet.as_view()),
    path("getStudentProfile/<int:student_id>/", StudentProfileViewset.as_view())
]