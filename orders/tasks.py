import logging

from celery import shared_task
from django.core.mail import send_mail

from orders.exceptions import OrderCanceled
from orders.serializers import OrderSerializer
from orders.services import OrderService
from stocks.services import StockService
from trading_platform.settings import EMAIL_HOST_USER

logger = logging.getLogger(__name__)
order_service = OrderService()
stock_service = StockService()


@shared_task
def check_open_orders():
    logger.info("[INFO] celery_task: check_open_orders")

    open_orders = order_service.filter_objs(status="open", manual=False)
    logger.info(f"[INFO] open orders for check: {len(open_orders)}")
    if open_orders.exists():
        for order in open_orders:
            if order_service.is_ready_to_close(order):
                try:
                    order_service.close_order(order)
                    logger.info(f"[INFO] celery_task: CLOSE ORDER#{order.id}")
                except OrderCanceled as e:
                    logger.info(f"[INFO] celery_task: CANCEL ORDER#{order.id}. {e.default_detail}")
                finally:
                    send_notification.delay(order_id=order.id)


@shared_task
def send_notification(order_id):
    order = order_service.get_by_id(obj_id=order_id)
    subject = f"Order {order.status}"
    message = (
        f"Order on {order.user_action_type} {order.stock} in quantity {order.quantity}\
              was {order.status}.\n"
        f"Closing price in moment of closing order: {order.closing_price}.\n"
        f"Your balance now: {order.user.balance}.\n"
        f"Stock price now: {stock_service.get_price(order.stock,order.user_action_type)}."
    )

    from_email = EMAIL_HOST_USER
    recipient_list = [order.user.email]

    send_mail(subject, message, from_email, recipient_list)
