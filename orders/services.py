from django.contrib.auth import get_user_model

from orders.models import Order
from orders.utils import check_user_balance, close_order
from stocks.models import Stock

User = get_user_model()


def create_order(**data_order) -> str:
    manual = data_order["manual"]
    quantity = data_order["quantity"]
    user_action_type = data_order["user_action_type"]
    stock_id = data_order["stock"]
    user_id = data_order["user"]
    order_type = data_order["order_type"]
    price_limit = data_order["price_limit"]

    user = User.objects.get(pk=user_id)
    stock = Stock.objects.get(pk=stock_id)

    check_user_balance(user, user_action_type, stock, quantity)

    order = Order.objects.create(
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
        balance = close_order(order)
        return f"Order created successfully. Your balance: {balance}."
    return "We notice you by mail when order will be closed."
