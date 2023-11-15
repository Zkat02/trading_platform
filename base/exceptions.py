from typing import Optional

from rest_framework.exceptions import APIException


class BaseClientException(APIException):
    status_code: int = 400
    default_detail: str = "Client Error occurred."

    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None) -> None:
        super().__init__(detail)
        if status_code is not None:
            self.status_code = status_code


class BaseServerException(APIException):
    status_code: int = 500
    default_detail: str = "Server Error occurred."

    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None) -> None:
        super().__init__(detail)
        if status_code is not None:
            self.status_code = status_code
