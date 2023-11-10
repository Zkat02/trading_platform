from typing import Type

from base.repositories import BaseRepository
from orders.models import Order


class OrderRepository(BaseRepository):
    def __init__(self, model: Type[Order]):
        super().__init__(model=model)

    def set_status(self, order: Order, status: Order.ORDER_TYPE) -> None:
        """
        Set the status of an order using the specified ORDER_TYPE.

        Args:
        order (Order): The order for which the status will be set.
        status (Order.ORDER_TYPE): The status type to be set for the order.

        Returns:
        None
        """
        order.status = status
        order.save()

    def close_order(self, order: Order, closing_price: float) -> None:
        """
        Close an order by setting the closing price and changing its status to 'closed'.

        Args:
        order (Order): The order to be closed.
        closing_price (float): The price at which the order is closed.

        Returns:
        None
        """
        order.closing_price = closing_price
        self.set_status(order=order, status="closed")
        order.save()
