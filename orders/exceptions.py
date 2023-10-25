from rest_framework.exceptions import PermissionDenied


class OrderDoNotCreated(PermissionDenied):
    detail = "Order wasn't created."

    def __init__(self, error_message):
        self.detail = error_message
        super().__init__(self.detail)
