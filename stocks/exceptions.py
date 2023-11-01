from base.exceptions import Base4xxException


class CreateSubcriptionException(Base4xxException):
    status_code = 401
    default_detail = "User is already subscribed to this stock."


class RemoveSubcriptionException(Base4xxException):
    status_code = 401
    default_detail = "User is not subscribed to this stock."


class PriceNotExist(Base4xxException):
    default_detail = 'Field user_action_type is not "buy" or "sell".'
