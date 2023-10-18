from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == "user"
        return False


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == "analyst"
        return False
