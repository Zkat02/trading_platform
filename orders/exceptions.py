from base.exceptions import BaseClientException


class OrderNotCreated(BaseClientException):
    status_code = 402
    default_detail = "Order wasn't created."


class OrderCanceled(BaseClientException):
    default_detail = "Order wasn canceled."
