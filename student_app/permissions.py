from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from core.authentication import decode
from .models import Student



class IsStudent(BasePermission):

    def has_permission(self, request, view):
        decoded=decode(model=Student,request=request)
        request.user=decoded[0]
        request.auth=decoded[1]
        return True 