import logging
from typing import List, Literal

from base.services import BaseService
from kafka_service.kafka_service import KafkaService
from stocks.exceptions import CreateSubcriptionException, PriceNotExist, RemoveSubcriptionException
from stocks.models import Stock
from stocks.repositories import StockRepository
from user_management.services import UserService

logger = logging.getLogger(__name__)


class StockService(BaseService):
    def __init__(self) -> None:
        """Initialize StockService instance."""
        self.user_service = UserService()
        self.kafka_service = KafkaService()
        super().__init__(model=Stock, repository=StockRepository)

    def create(self, **kwargs) -> Stock:
        """Create Stock.
        Send to kafka symbol of stock that need to be created at mongodb for regular checks of price.

        Kwargs:
        - symbol (str): The symbol of the stock.
        - name (str): The name of the stock.
        - price_per_unit_sail (float): The price per unit of sail.
        - price_per_unit_buy (float): The price per unit of buy.
        - available_quantity (int): The available quantity of the stock.

        Returns:
        - Stock: The created stock.

        """
        symbol = kwargs.get("symbol")
        self.kafka_service.send_stock_symbols_to_kafka(symbol)
        return self.repository.create(**kwargs)

    def update_stock_prices(self):
        """
        Update stock prices from kafka.
        """
        logger.info("Start update prices")
        for kafka_data in self.kafka_service.read_stock_prices_from_kafka():
            stocks = kafka_data["stocks"]
            for stock in stocks:
                symbol = stock["symbol"]
                new_stock_prices = {
                    "price_per_unit_sail": stock["sell_price"],
                    "price_per_unit_buy": stock["buy_price"],
                }
                stock = self.find_by_symbol(symbol)
                if stock is None:
                    continue

                stock = self.update(obj_id=stock.id, **new_stock_prices)
                logger.info(
                    f"Stock {symbol} were updated successfully: {stock.price_per_unit_sail},{stocks.price_per_unit_buy}"
                )

    def send_stock_symbols_to_kafka(self):
        symbols = self.get_all_symbols()
        logger.info("Symbols from db:", symbols)
        if symbols:
            self.kafka_service.send_stock_symbols_to_kafka(symbols=symbols)

    def get_all_symbols(self):
        stocks = self.get_all()
        symbols = []
        for stock in stocks:
            symbols.append(stock.symbol)
        return symbols

    def find_by_symbol(self, symbol: str) -> Stock:
        """
        Find a stock by its symbol.

        Args:
        - symbol (str): The symbol of the stock.

        Returns:
        - Stock: The found stock or None if it isn't exsist.
        """
        return self.repository.find_by_symbol(symbol)

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

    def set_price(self, stock: Stock, action: Literal["sell", "buy"], new_value: float) -> None:
        """
        Set the price based on the action.

        Args:
        - stock (Stock): The stock object.
        - action (Literal["sell", "buy"]): Action type to determine the price.
        - new_value (float): new price.

        Returns:
        - None.

        Raises:
        - PriceNotExist: If the action is not 'sell' or 'buy'.
        """
        if action == "sell":
            return self.repository.set_price_per_unit_buy(stock, new_value)
        if action == "buy":
            return self.repository.set_price_per_unit_sail(stock, new_value)

    def can_buy(self, stock: Stock, quantity: int) -> bool:
        """
        Check available_quantity before buy.

        Args:
        - stock (Stock): The stock object.
        - quantity (int): Quantity for buy.

        Returns:
        - True: available_quantity enough.
        - False: available_quantity not enough.
        """
        if stock.available_quantity >= quantity:
            return True
        return False

    def set_available_quantity(self, stock: Stock, new_value: int) -> None:
        """
        Check available_quantity before buy.

        Args:
        - stock (Stock): The stock object.
        - quantity (int): Quantity for buy.

        Returns:
        - True: available_quantity enought.
        - False: available_quantity not enought.
        """
        """
        Set new value to available_quantity.

        Args:
        - stock (Stock): The stock object.
        - new_value (int): new quantity.

        Returns:
        - None
        """
        return self.repository.set_available_quantity(stock, new_value)
