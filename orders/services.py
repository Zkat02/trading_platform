from base.services import BaseService
from orders.exceptions import OrderCanceled, OrderDoNotCreated
from orders.repositories import OrderRepository
from stocks.services import StockService
from user_management.exceptions import SubtractBalanceException
from user_management.services import UserService


class OrderService(BaseService):
    def __init__(self):
        self.repository = OrderRepository()
        self.user_service = UserService()
        self.stock_service = StockService()

    def create_order(self, **kwargs):
        user_id = kwargs.get("user_id")
        stock_id = kwargs.get("stock_id")
        quantity = kwargs.get("quantity")
        user_action_type = kwargs.get("user_action_type")
        order_type = kwargs.get("order_type")
        price_limit = kwargs.get("price_limit")
        manual = kwargs.get("manual")

        user = self.user_service.get_user_by_id(user_id=user_id)
        stock = self.stock_service.get_by_id(obj_id=stock_id)

        self.check_user_balance(quantity, user_action_type, stock, user, price_limit)

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
            balance = self.close_order(order=order)
            return f"Order closed successfully. Closing price {order.closing_price}.\
                  Your balance: {balance}."
        return "We notice you by mail when order will be closed."

    def cancel_order(self, order):
        print("order canceled.")
        self.repository.set_status(order=order, status="canceled")

    def close_order(self, order):
        balance = self.calculate_user_balance(order)
        print(balance)
        stock = order.stock
        closing_price = self.stock_service.get_price(stock=stock, action=order.user_action_type)
        self.repository.close_order(order, closing_price)
        return balance

    def check_user_balance(self, **kwargs):
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
            raise OrderDoNotCreated("Order do not create: insufficient balance.")
        raise OrderDoNotCreated('Field user_action_type is not "buy" or "sell".')

    def calculate_user_balance(self, order):
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
        raise OrderDoNotCreated(
            'Order not created: field <user_action_type> is not "buy" or "sell".'
        )

    def order_cancel_notification(self, order):
        pass

    def order_close_notification(self, order):
        pass

    def filter_orders(self, **kwargs):
        return self.repository.filter_orders(**kwargs)

    def check_condition_for_close(self, order):
        order_type = order.order_type
        price_limit = order.price_limit
        user_action_type = order.user_action_type

        current_stock_price = self.stock_service.get_price(order.stock, user_action_type)

        if current_stock_price >= price_limit:
            # quick buy or sell
            if (order_type == "short" and order.user_action_type == "sell") or (
                order_type == "short" and order.user_action_type == "buy"
            ):
                return True
        if current_stock_price <= price_limit:
            # long sell or buy
            if (order_type == "long" and order.user_action_type == "buy") or (
                order_type == "long" and order.user_action_type == "sell"
            ):
                return True
        return False
