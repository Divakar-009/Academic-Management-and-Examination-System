from django.urls import include, path
from rest_framework import routers
from student_app.views import *

router=routers.DefaultRouter()
router.register(r'studentRegist',StudentRegisterView)

urlpatterns =router.urls+[
    path('studentLog/',StudentLoginView.as_view()),
    path('assignments/<int:assignment_id>/',StudentAssignmentApiview.as_view()),
    path('assignments/<int:assignment_id>/submit/',submitAssignmentAPIView.as_view()),
    
]