from rest_framework.permissions import BasePermission

from user_management.exceptions import UserBlockedException


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return True
        return False


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return request.user.role == "user"
        return False


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_active:
                return request.user.role == "analyst"
        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            if request.user.is_active:
                return request.user.role == "admin"
        return False


class IsAdminOrAnalyst(BasePermission):
    def has_permission(self, request, view):
        is_admin = IsAdmin().has_permission(request, view)
        is_analyst = IsAnalyst().has_permission(request, view)
        return is_admin or is_analyst


class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        is_admin = IsAdmin().has_permission(request, view)
        is_user = IsUser().has_permission(request, view)
        return is_admin or is_user


class CanCancelOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.is_active:
                if request.user.is_superuser and request.user.role == "admin":
                    return True
                if obj.user == request.user:
                    return True
                return False
