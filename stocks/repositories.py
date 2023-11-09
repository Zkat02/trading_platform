from decimal import Decimal
from django.db.models import QuerySet
from base.repositories import BaseRepository
from stocks.models import Stock
from user_management.models import CustomUser as User


class StockRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Stock)

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

    def set_price_per_unit_buy(self, stock: Stock, new_value: Decimal) -> Decimal:
        """
        Set the price per unit for buying a stock.

        Args:
        - stock (Stock): The stock object.
        - new_value (Decimal): The new value to set.

        Returns:
        - Decimal: The updated price per unit for buying the stock.
        """
        stock.price_per_unit_buy = new_value
        stock.save()
        return stock.price_per_unit_buy

    def set_price_per_unit_sell(self, stock: Stock, new_value: Decimal) -> Decimal:
        """
        Set the price per unit for selling a stock.

        Args:
        - stock (Stock): The stock object.
        - new_value (Decimal): The new value to set.

        Returns:
        - Decimal: The updated price per unit for selling the stock.
        """
        stock.set_price_per_unit_sail = new_value
        stock.save()
        return stock.set_price_per_unit_sail
