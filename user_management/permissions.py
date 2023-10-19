from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "user"


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "analyst"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"
