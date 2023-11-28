from decimal import Decimal
from typing import Type

from django.db.models import QuerySet

from base.repositories import BaseRepository
from stocks.models import Stock
from user_management.models import CustomUser as User


class StockRepository(BaseRepository):
    def __init__(self, model: Type[Stock]):
        super().__init__(model=model)

    def check_subscription(self, user: User, stock_id: int) -> bool:
        """
        Check if a user is subscribed to a stock.

        Args:
        - user (User): The user object.
        - stock_id (int): The ID of the stock.

        Returns:
        - bool: True if the user is subscribed to the stock, False otherwise.
        """
        return user.subscriptions.filter(pk=stock_id).exists()

    def get_user_subscriptions(self, user: User) -> QuerySet[Stock]:
        """
        Get all subscriptions of a user.

        Args:
        - user (User): The user object.

        Returns:
        - QuerySet[Stock]: QuerySet of stock subscriptions for the user.
        """
        return user.subscriptions

    def set_price_per_unit_buy(self, stock: Stock, new_value: Decimal) -> None:
        """
        Set the price per unit for buying a stock.

        Args:
        - stock (Stock): The stock object.
        - new_value (Decimal): The new value to set.

        Returns:
        - None.
        """
        stock.price_per_unit_buy = new_value
        stock.save()

    def set_price_per_unit_sell(self, stock: Stock, new_value: Decimal) -> None:
        """
        Set the price per unit for selling a stock.

        Args:
        - stock (Stock): The stock object.
        - new_value (Decimal): The new value to set.

        Returns:
        - None.
        """
        stock.set_price_per_unit_sail = new_value
        stock.save()

    def set_available_quantity(self, stock: Stock, new_value: int) -> None:
        """
        Set the available_quantity.

        Args:
        - stock (Stock): The stock object.
        - new_value (int): The new value to set.

        Returns:
        - None.
        """
        stock.available_quantity = new_value
        stock.save()

    def find_by_symbol(self, symbol: str) -> Stock:
        """
        Find a stock by its symbol.

        Args:
        - symbol (str): The symbol of the stock.

        Returns:
        - Stock: The found stock or None if not found.
        """
        try:
            stock = self.model.objects.get(symbol=symbol)
            return stock
        except Stock.DoesNotExist:
            return None
