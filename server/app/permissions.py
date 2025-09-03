from rest_framework import permissions
from .models import CustomUser

# Document: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

class IsVerificated(permissions.BasePermission):
    message = 'You must verify your account before performing this action.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not getattr(request.user, "isVerificated", False):
            return False

        return True