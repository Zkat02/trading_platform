from typing import Union

from django.db.models import QuerySet

from base.services import BaseService
from inventory.exceptions import InventoryException, InventoryUpdateException
from inventory.models import Inventory
from inventory.repositories import InventoryRepository
from orders.models import Order
from stocks.models import Stock
from stocks.services import StockService
from user_management.models import CustomUser as User
from user_management.services import UserService


class InventoryService(BaseService):
    def __init__(self) -> None:
        self.user_service = UserService()
        self.stock_service = StockService()
        super().__init__(model=Inventory, repository=InventoryRepository)

    def get_user_inventory(self, user_id: int) -> QuerySet[Inventory]:
        """
        Get the user's inventory - all stocks that user own.
        Args:
        - user_id (int): The ID of the user.
        Returns:
        - QuerySet[Inventory]: QuerySet of the user's inventory.
        """
        user = self.user_service.get_by_id(obj_id=user_id)
        return self.repository.filter_objs(user=user)

    def get_user_stock_inventory(self, user_id: int, stock_id: int) -> Inventory:
        """
        Get the user's inventory to specific stock.
        Args:
        - user_id (int): The ID of the user.
        - stock_id (int): The ID of the stock.
        Returns:
        - QuerySet[Inventory]: QuerySet of the user's inventory to specific stock.
        """
        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.stock_service.get_by_id(obj_id=stock_id)
        if self.stock_in_inventory_exists(user=user, stock=stock):
            return self.repository.filter_objs(user=user, stock=stock).first()

    def stock_in_inventory_exists(self, user: User, stock: Stock) -> bool:
        """
        Check if an inventory exists for a user and stock.
        Args:
        - user (User): The user object.
        - stock (Stock): The stock object.
        Returns:
        - bool: True if the inventory exists, False otherwise.
        """
        return self.repository.filter_objs(user=user, stock=stock).exists()

    def is_inventory_quantity_enough(self, inventory, quantity) -> bool:
        return inventory.quantity >= quantity

    def can_sell_stock(self, user_id: int, stock_id: int, quantity: int) -> bool:
        """
        Check user's inventory: if stock is available for sell in this quantity.

        Args:
        - stock (Stock): The stock object.
        - quantity (int): Quantity for buy.

        Returns:
        True: if user own enough stock quantity, otherwise False.
        """
        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.stock_service.get_by_id(obj_id=stock_id)
        if self.stock_in_inventory_exists(user=user, stock=stock):
            inventory = self.get_user_stock_inventory(user_id=user_id, stock_id=stock_id)
            return self.is_inventory_quantity_enough(inventory=inventory, quantity=quantity)
        raise InventoryException(f"InventoryException: You not own this stock {stock}.")

    def update_inventory(
        self,
        user_id: int,
        stock_id: int,
        quantity: int,
        action: Union[Order.USER_ACTION_TYPE.BUY, Order.USER_ACTION_TYPE.SELL],
    ) -> None:
        """
        Update the quantity of an inventory.
        If action is BUY quantity increase on value of quantity,
        if action is SELL quantity decrease on value of quantity.
        If inventory is not existing then create it.
        Args:
        - user_id (int): The ID of the user.
        - stock_id (int): The ID of the stock.
        - quantity (int): The quantity to update.
        - action (str): The user action type (BUY,SELL).
        """
        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.stock_service.get_by_id(obj_id=stock_id)
        if self.stock_in_inventory_exists(user=user, stock=stock):
            inventory = self.repository.filter_objs(user=user, stock=stock).first()
            if action == Order.USER_ACTION_TYPE.BUY:
                self.repository.add_quantity(inventory)
                inventory.quantity += quantity
                inventory.save()
                return

            elif action == Order.USER_ACTION_TYPE.SELL:
                self.repository.subtract_quantity(inventory)
                inventory.quantity -= quantity
                inventory.save()
                return
        else:
            if action == Order.USER_ACTION_TYPE.BUY:
                Inventory.objects.create(user=user, stock=stock, quantity=quantity)
            elif action == Order.USER_ACTION_TYPE.SELL:
                raise InventoryUpdateException(
                    "InventoryUpdateException: You do not own this stock."
                )
                # raise InsufficientStockException("Not enough stocks available for purchase.")

    def add_quantity(self, user_id: int, stock_id: int, quantity: int) -> None:
        inventory = self.get_user_stock_inventory(user_id, stock_id)
        if inventory is None:
            inventory = self.create(
                user=self.user_service.get_by_id(user_id),
                stock=self.stock_service.get_by_id(stock_id),
                quantity=quantity,
            )
            return
        self.repository.add_quantity(inventory=inventory, quantity=quantity)

    def subtract_quantity(self, user_id: int, stock_id: int, quantity: int) -> None:
        inventory = self.get_user_stock_inventory(user_id, stock_id)
        self.repository.subtract_quantity(inventory=inventory, quantity=quantity)
