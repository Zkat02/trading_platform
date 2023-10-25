from celery import shared_task
from django.core.mail import send_mail

from orders.models import Order
from orders.utils import close_order
from trading_platform.settings import EMAIL_HOST_USER


@shared_task
def check_open_orders():
    print("celery_task: check_open_orders")
    open_orders = Order.objects.filter(status="open", manual=False)
    if open_orders.exists():
        for order in open_orders:
            stock = order.stock
            order_type = order.order_type
            if order.user_action_type == "buy":
                current_price = stock.price_per_unit_sail
            if order.user_action_type == "sell":
                current_price = stock.price_per_unit_buy
            if order_type == "short":
                if current_price <= order.price_limit:
                    close_order(order)
                    send_order_closed_notification.delay(order.id, current_price)
            elif order_type == "long":
                if current_price >= order.price_limit:
                    close_order(order)
                    send_order_closed_notification.delay(order.id, current_price)


@shared_task
def send_order_closed_notification(order_id, current_price):
    order = Order.objects.get(id=order_id)
    subject = "Closed order"
    message = (
        f"Order on {order.user_action_type} {order.stock} in quantity {order.quantity} was closed.\n"
        f"Total price: {current_price * order.quantity}.\n"
        f"Your balance now: {order.user.balance}.\n"
        f"Stock price in moment of closing order: {current_price}."
    )

    from_email = EMAIL_HOST_USER
    recipient_list = [order.user.email]

    send_mail(subject, message, from_email, recipient_list)
