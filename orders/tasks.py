import logging

import boto3
from botocore.exceptions import NoCredentialsError
from celery import shared_task
from django.conf import settings

from orders.services import OrderService
from stocks.services import StockService
from trading_platform.settings import EMAIL_HOST_USER

logger = logging.getLogger(__name__)


@shared_task
def check_open_orders():
    order_service = OrderService()

    logger.info("[INFO] celery_task: check_open_orders")

    open_orders = order_service.filter_objs(status="open", manual=False)
    logger.info(f"[INFO] open orders for check: {len(open_orders)}")
    if open_orders.exists():
        for order in open_orders:
            if order_service.is_ready_to_close(order):
                order_service.close_order(order)
                logger.info(
                    f"[INFO] celery_task(check_open_orders): ORDER#{order.id} {order.status}"
                )
                send_notification.delay(order_id=order.id)


@shared_task
def send_notification(order_id: int):
    order_service = OrderService()
    stock_service = StockService()

    order = order_service.get_by_id(obj_id=order_id)
    subject = f"Order {order.status}"
    body = (
        f"Order on {order.user_action_type} {order.stock} in quantity {order.quantity}\
              was {order.status}.\n"
        f"Closing price in moment of closing order: {order.closing_price}.\n"
        f"Your balance now: {order.user.balance}.\n"
        f"Stock price now: {stock_service.get_price(order.stock,order.user_action_type)}."
    )

    from_email = EMAIL_HOST_USER
    recipient_list = [order.user.email]

    logger.info(f"[INFO] celery_task (send_notification): ")

    ses_client = boto3.client(
        "ses",
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        region_name=settings.AWS_DEFAULT_REGION,
        endpoint_url=f"http://host.docker.internal:{settings.LOCALSTACK_PORT}",
    )

    ses_client.verify_email_identity(EmailAddress=settings.EMAIL_HOST_USER)

    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={"ToAddresses": recipient_list},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
    except NoCredentialsError:
        logger.info("Credentials not available")
        return False
    else:
        logger.info("Email sent! Message ID: {}".format(response["MessageId"]))
        return True
