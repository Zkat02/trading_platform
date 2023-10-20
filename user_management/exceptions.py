from rest_framework.exceptions import PermissionDenied


class UserBlockedException(PermissionDenied):
    default_detail = "User is blocked."
