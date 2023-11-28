from typing import Type

from django.db.models import QuerySet

from base.repositories import BaseRepository
from inventory.models import Inventory


class InventoryRepository(BaseRepository):
    """Repository for inventory"""

    def __init__(self, model: Type[Inventory]):
        super().__init__(model=model)

    def get_user_inventory(self, user) -> QuerySet[Inventory]:
        return self.model.query.filter_by(user=user)

    def add_quantity(self, inventory: Inventory, quantity: int) -> None:
        inventory.quantity += quantity
        inventory.save()

    def subtract_quantity(self, inventory: Inventory, quantity: int) -> None:
        if inventory.quantity < quantity:
            raise Exception("You don't own that many stocks in your inventory.")
        if inventory.quantity == quantity:
            self.delete(inventory)
            return
        inventory.quantity -= quantity
        inventory.save()
