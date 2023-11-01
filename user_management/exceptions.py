from rest_framework.exceptions import PermissionDenied

from base.exceptions import Base4xxException


class AuthenticationFailedException(Base4xxException):
    status_code = 401
    default_detail = "Authentication failed."


class ChangeBalanceException(Base4xxException):
    status_code = 402
    default_detail = "Balance was not changed."


class SubtractBalanceException(Base4xxException):
    status_code = 402
    default_detail = "Insufficient balance."


class UserBlockedException(PermissionDenied):
    default_detail = "User is blocked."


class DoNotBlockException(Base4xxException):
    default_detail = "User do not blocked."


class DoNotUnlockException(Base4xxException):
    default_detail = "User do not unlocked."
