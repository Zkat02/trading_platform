from typing import List, Literal

from base.services import BaseService
from stocks.exceptions import CreateSubcriptionException, PriceNotExist, RemoveSubcriptionException
from stocks.models import Stock
from stocks.repositories import StockRepository
from user_management.services import UserService


class StockService(BaseService):
    def __init__(self) -> None:
        """Initialize StockService instance."""
        self.user_service = UserService()
        super().__init__(model=Stock, repository=StockRepository)

    def check_subscription(self, user_id: int, stock_id: int) -> bool:
        """
        Check if a user is subscribed to a specific stock.

        Args:
        - user_id (int): The ID of the user.
        - stock_id (int): The ID of the stock.

        Returns:
        - bool: True if the user is subscribed to the stock, False otherwise.
        """

        user = self.user_service.get_by_id(user_id)
        subscribed = self.repository.check_subscription(user, stock_id)
        if subscribed:
            return True
        return False

    def create_subscription(self, user_id: int, stock_id: int) -> bool:
        """
        Create a subscription for a user to a stock.

        Args:
        - user_id (int): The ID of the user.
        - stock_id (int): The ID of the stock.

        Returns:
        - bool: True if the subscription is successfully created.
        """
        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.get_by_id(obj_id=stock_id)

        if self.check_subscription(user_id, stock_id):
            raise CreateSubcriptionException("You are already subscribed to this stock.")

        user.subscriptions.add(stock)
        return True

    def remove_subscription(self, user_id: int, stock_id: int) -> bool:
        """
        Remove a subscription of a user to a stock.

        Args:
        - user_id (int): The ID of the user.
        - stock_id (int): The ID of the stock.

        Returns:
        - bool: True if the subscription is successfully removed.

        Raises:
        - RemoveSubcriptionException: If the user is not subscribed to the stock.
        """

        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.get_by_id(obj_id=stock_id)

        if self.check_subscription(user_id, stock_id):
            user.subscriptions.remove(stock)
            return True
        raise RemoveSubcriptionException("You are not subscribed to this stock.")

    def get_all_user_subscriptions(self, user_id: int) -> List[Stock]:
        """
        Get all subscriptions of a user.

        Args:
        - user_id (int): The ID of the user.

        Returns:
        - List[Stock]: List of stock subscriptions for the user.
        """

        user = self.user_service.get_by_id(obj_id=user_id)
        return self.repository.get_user_subscriptions(user=user)

    def get_price(self, stock: Stock, action: Literal["sell", "buy"]) -> float:
        """
        Return the price based on the action.

        Args:
        - stock (Stock): The stock object.
        - action (Literal["sell", "buy"]): Action type to determine the price.

        Returns:
        - float: Price of the stock based on the action.

        Raises:
        - PriceNotExist: If the action is not 'sell' or 'buy'.
        """
        if action == "sell":
            return stock.price_per_unit_buy
        if action == "buy":
            return stock.price_per_unit_sail
        raise PriceNotExist()

    def set_price(self, stock: Stock, action: Literal["sell", "buy"], new_value: float) -> float:
        """
        Set the price based on the action.

        Args:
        - stock (Stock): The stock object.
        - action (Literal["sell", "buy"]): Action type to determine the price.
        - new_value (float): new price.

        Returns:
        - float: Price of the stock based on the action.

        Raises:
        - PriceNotExist: If the action is not 'sell' or 'buy'.
        """
        if action == "sell":
            return self.repository.set_price_per_unit_buy(stock, new_value)
        if action == "buy":
            return self.repository.set_price_per_unit_sail(stock, new_value)
