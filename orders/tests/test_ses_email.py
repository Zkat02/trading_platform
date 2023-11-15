import logging

from django.contrib.auth import get_user_model
from django.test import TestCase

from inventory.services import InventoryService
from orders.models import Order
from orders.services import OrderService
from orders.tasks import send_notification
from stocks.models import Stock
from stocks.services import StockService
from trading_platform.celery import app as celery_app
from user_management.services import UserService

User = get_user_model()
logger = logging.getLogger(__name__)


class BaseOrderTestCase(TestCase):
    user_service = UserService()

    def setUp(self):
        user_data = {
            "username": "user_test",
            "password": "user_password",
            "email": "user_test@gmail.com",
            "role": "user",
        }

        self.user = User.objects.create_user(**user_data)
        self.user_jwt_token = self.user_service.authentificate_user(
            self.user.username, user_data["password"]
        )

        self.stock = Stock.objects.create(
            name="test Stock 1",
            symbol="tFS1",
            price_per_unit_sail=120,
            price_per_unit_buy=110,
            available_quantity=10,
        )


class CreateOrderViewTestCase(BaseOrderTestCase):
    order_service = OrderService()
    stock_service = StockService()
    inventory_service = InventoryService()

    def setUp(self):
        super().setUp()
        order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": False,
            "user_action_type": Order.USER_ACTION_TYPE.BUY,
            "price_limit": 100,
            "order_type": Order.ORDER_TYPE.LONG,
            "status": "closed",
            "closing_price": 120,
        }
        self.order = Order.objects.create(**order_data)

        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_ses_send_email(self):
        task = send_notification.apply(args=[self.order.id])
        task.get()
        self.assertEqual(task.state, "SUCCESS")

    def test_ses(self):
        import boto3
        from django.conf import settings

        client = boto3.client(
            "ses",
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            region_name=settings.AWS_DEFAULT_REGION,
            endpoint_url=f"http://host.docker.internal:{settings.LOCALSTACK_PORT}",
        )
        client.verify_email_identity(EmailAddress=settings.EMAIL_HOST_USER)

        client.send_email(
            Destination={
                "ToAddresses": ["recipient1@domain.com", "recipient2@domain.com"],
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": "email body string",
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": "email subject string",
                },
            },
            Source="zkatdjango@gmail.com",
        )
