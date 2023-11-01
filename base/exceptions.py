from rest_framework.exceptions import APIException


class Base4xxException(APIException):
    status_code = 400
    default_detail = "Client Error occurred."

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail)
        if status_code is not None:
            self.status_code = status_code


class Base5xxException(APIException):
    status_code = 500
    default_detail = "Server Error occurred."

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail)
        if status_code is not None:
            self.status_code = status_code
