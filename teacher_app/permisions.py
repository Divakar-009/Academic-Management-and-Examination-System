from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from core.authentication import decode
from .models import TecherRegist
from .serializers import TeacherSerializer


class IsJWTAuthorized(BasePermission):

    def has_permission(self, request, view):
        decoded=decode(model=TecherRegist,request=request)
        request.user=decoded[0]
        request.auth=decoded[1]
        return True 