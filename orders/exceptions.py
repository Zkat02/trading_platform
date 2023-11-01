from base.exceptions import Base4xxException


class OrderDoNotCreated(Base4xxException):
    status_code = 402
    default_detail = "Order wasn't created."


class OrderCanceled(Base4xxException):
    default_detail = "Order wasn canceled."
