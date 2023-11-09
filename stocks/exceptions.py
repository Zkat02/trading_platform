from base.exceptions import BaseClientException


class CreateSubcriptionException(BaseClientException):
    status_code = 401
    default_detail = "User is already subscribed to this stock."


class RemoveSubcriptionException(BaseClientException):
    status_code = 401
    default_detail = "User is not subscribed to this stock."


class PriceNotExist(BaseClientException):
    default_detail = 'Field user_action_type is not "buy" or "sell".'
