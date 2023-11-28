from base.exceptions import BaseClientException


class InventoryException(BaseClientException):
    default_detail = "Inventory exception."


class InventoryUpdateException(BaseClientException):
    default_detail = "Inventory not updated."
