from typing import Literal

from base.services import BaseService
from stocks.exceptions import CreateSubcriptionException, PriceNotExist, RemoveSubcriptionException
from stocks.repositories import StockRepository
from user_management.services import UserService


class StockService(BaseService):
    def __init__(self):
        self.repository = StockRepository()
        self.user_service = UserService()

    def check_subscription(self, user_id, stock_id):
        user = self.user_service.get_by_id(user_id)
        subscribed = self.repository.check_subscription(user, stock_id)
        if subscribed:
            return True
        return False

    def check_subscription_message(self, user_id, stock_id):
        if self.check_subscription(user_id, stock_id):
            message = "You subscribe to this stock."
            return message
        message = "You have not subscribed to this stock yet."
        return message

    def create_subscription(self, user_id, stock_id):
        user = self.user_service.get_user_by_id(user_id=user_id)
        stock = self.get_by_id(obj_id=stock_id)

        if self.check_subscription(user_id, stock_id):
            raise CreateSubcriptionException("You are already subscribed to this stock.")

        user.subscriptions.add(stock)
        return True

    def remove_subscription(self, user_id, stock_id):
        user = self.user_service.get_user_by_id(user_id=user_id)
        stock = self.get_by_id(obj_id=stock_id)

        if self.check_subscription(user_id, stock_id):
            user.subscriptions.remove(stock)
            return True
        raise RemoveSubcriptionException("You are not subscribed to this stock.")

    def get_all_user_subscriptions(self, user_id):
        user = self.user_service.get_user_by_id(user_id=user_id)
        return self.repository.get_user_subscriptions(user=user)

    def get_price(self, stock, action: Literal["sell", "buy"]):
        """
        return price by action: "sell" | "buy"
        user buy stock: price_per_unit_sail
        user sell stock: price_per_unit_buy
        """
        if action == "sell":
            return stock.price_per_unit_buy
        if action == "buy":
            return stock.price_per_unit_sail
        raise PriceNotExist()
