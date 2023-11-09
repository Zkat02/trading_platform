from rest_framework.exceptions import PermissionDenied

from base.exceptions import BaseClientException


class AuthenticationFailedException(BaseClientException):
    status_code = 401
    default_detail = "Authentication failed."


class ChangeBalanceException(BaseClientException):
    status_code = 402
    default_detail = "Balance was not changed."


class SubtractBalanceException(BaseClientException):
    status_code = 402
    default_detail = "Insufficient balance."


class UserBlockedException(PermissionDenied):
    default_detail = "User is blocked."


class DoNotBlockException(BaseClientException):
    default_detail = "User do not blocked."


class DoNotUnblockException(BaseClientException):
    default_detail = "User do not unblocked."
