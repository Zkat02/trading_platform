from rest_framework.permissions import BasePermission

from user_management.exceptions import UserBlockedException


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return True
            raise UserBlockedException()
        return False


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return request.user.role == "user"
            raise UserBlockedException()
        return False


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return request.user.role == "analyst"
            raise UserBlockedException()
        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            if request.user.is_active:
                return request.user.role == "admin"
            raise UserBlockedException()
        return False
