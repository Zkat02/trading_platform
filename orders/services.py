import logging
from typing import Optional

from base.services import BaseService
from orders.exceptions import OrderCanceled, OrderNotCreated
from orders.models import Order
from orders.repositories import OrderRepository
from orders.serializers import OrderSerializer
from stocks.services import StockService
from user_management.exceptions import SubtractBalanceException
from user_management.services import UserService

logger = logging.getLogger(__name__)


class OrderService(BaseService):
    def __init__(self) -> None:
        """Initialize OrderService instance."""
        self.user_service = UserService()
        self.stock_service = StockService()
        super().__init__(model=Order, repository=OrderRepository)

    def create_order(self, **kwargs) -> Optional[Order]:
        """
        Create a new order based on provided parameters.

        Args:
        **kwargs: Arguments for order creation:
            - user_id: Integer, user identifier.
            - stock_id: Integer, stock identifier.
            - quantity: Integer, quantity of stock.
            - user_action_type: String, user action type (buy or sell).
            - order_type: String, type of the order (long or short).
            - price_limit: Float, price limit if specified.
            - manual: Boolean, whether the order is manual - True or automatic - False.


        Returns:
        Optional[Order]: The created order if successful, otherwise None.
        """
        user_id = kwargs.get("user_id")
        stock_id = kwargs.get("stock_id")
        quantity = kwargs.get("quantity")
        user_action_type = kwargs.get("user_action_type")
        order_type = kwargs.get("order_type")
        price_limit = kwargs.get("price_limit")
        manual = kwargs.get("manual")

        user = self.user_service.get_by_id(obj_id=user_id)
        stock = self.stock_service.get_by_id(obj_id=stock_id)

        data_to_check = {
            "quantity": quantity,
            "user_action_type": user_action_type,
            "stock": stock,
            "user": user,
            "price_limit": price_limit,
        }
        self.check_user_balance(**data_to_check)

        order = self.repository.create(
            user=user,
            stock=stock,
            quantity=quantity,
            status="open",
            manual=manual,
            user_action_type=user_action_type,
            price_limit=price_limit,
            order_type=order_type,
        )

        if order.manual:
            self.close_order(order=order)
        return order

    def can_cancel_order(self, order: Order) -> bool:
        """
        Check the ability to cancel an order.

        Args:
        order (Order): The order to be canceled.
        Returns: True if order can be canceled, otherwise False.
        """
        return order.status == Order.ORDER_STATUS.OPEN

    def cancel_order(self, order: Order) -> None:
        """
        Cancel an order.

        Args:
        order (Order): The order to be canceled.
        Returns: None
        """
        self.repository.set_status(order=order, status="canceled")

    def close_order(self, order: Order) -> Optional[float]:
        """
        Close an order and return the balance.

        Args:
        order (Order): The order to be closed.

        Returns:
        Optional[float]: The user balance after close.
        """

        balance = self.calculate_user_balance(order)
        stock = order.stock
        closing_price = self.stock_service.get_price(stock=stock, action=order.user_action_type)
        self.repository.close_order(order, closing_price)
        return balance

    def check_user_balance(self, **kwargs) -> bool:
        """
        Check if the user has enough balance to create the order.

        Args:
        **kwargs: Arguments for checking user balance:
            - user: User object.
            - stock: Stock object.
            - quantity: Integer, quantity of stock.
            - user_action_type: String, user action type (buy or sell).
            - price_limit: Float, price limit if specified.

        Returns:
        bool: True if the user has enough balance to create the order,
        otherwise raises OrderNotCreated.
        """

        user = kwargs.get("user")
        stock = kwargs.get("stock")
        quantity = kwargs.get("quantity")
        user_action_type = kwargs.get("user_action_type")
        price_limit = kwargs.get("price_limit")

        if user_action_type == "sell":
            return True

        stock_sell_price = stock.price_per_unit_sail

        if price_limit is not None:
            stock_sell_price = price_limit
        if user_action_type == "buy":
            if user.balance >= quantity * stock_sell_price:
                return True
            raise OrderNotCreated("Order do not create: insufficient balance.")
        raise OrderNotCreated('Field user_action_type is not "buy" or "sell".')

    def calculate_user_balance(self, order: Order) -> Optional[float]:
        """
        Calculate user balance based on the order.

        Args:
        order (Order): The order for which to calculate the user's balance.

        Returns:
        Optional[float]: The updated balance if the action was successful, otherwise None.
        """

        if order.user_action_type == "buy":
            try:
                total_price = order.quantity * order.stock.price_per_unit_sail
                return self.user_service.subtract_from_balance(order.user.id, total_price)

            except SubtractBalanceException:
                self.cancel_order(order)
                raise OrderCanceled("Order canceled: insufficient balance.")

        elif order.user_action_type == "sell":
            total_price = order.quantity * order.stock.price_per_unit_buy
            return self.user_service.add_to_balance(order.user.id, total_price)
        raise OrderNotCreated('Order not created: field <user_action_type> is not "buy" or "sell".')

    def order_cancel_notification(self, order: Order) -> None:
        pass

    def order_close_notification(self, order: Order) -> None:
        pass

    def is_ready_to_close(self, order: Order) -> bool:
        """
        Check if the order is ready to be closed.

        Args:
        order (Order): The order to check for closure readiness.

        Returns:
        bool: True if the order is ready to close, otherwise False.
        """
        order_type = order.order_type
        price_limit = order.price_limit
        user_action_type = order.user_action_type

        current_stock_price = self.stock_service.get_price(order.stock, user_action_type)
        logger.info(
            f"""[INFO] is_ready_to_close
        current_stock_price: {current_stock_price},
        price_limit: {price_limit},
        order_type: {order_type} user_action_type: {user_action_type}"""
        )

        if current_stock_price >= price_limit:
            # quick buy or sell
            if (
                order_type == Order.ORDER_TYPE.SHORT
                and user_action_type == Order.USER_ACTION_TYPE.SELL
            ) or (
                order_type == Order.ORDER_TYPE.SHORT
                and user_action_type == Order.USER_ACTION_TYPE.BUY
            ):
                return True
        if current_stock_price <= price_limit:
            # long sell or buy
            if (
                order_type == Order.ORDER_TYPE.LONG
                and user_action_type == Order.USER_ACTION_TYPE.BUY
            ) or (
                order_type == Order.ORDER_TYPE.LONG
                and user_action_type == Order.USER_ACTION_TYPE.SELL
            ):
                return True
        logger.info(f"[INFO] is_ready_to_close - FALSE: Order#{order.id} not ready")
        return False
