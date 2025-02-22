# permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with user_type 1 (AdminUser).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 1
    
