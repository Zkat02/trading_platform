from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import OrderService
from orders.tasks import check_open_orders
from orders.views import (CancelOrderView, CreateOrderView, CurrentUserOrderList, OrderList,
                          UserOrderList)
from stocks.models import Stock
from stocks.services import StockService
from trading_platform.celery import app as celery_app
from user_management.services import UserService

User = get_user_model()


class BaseOrderTestCase(TestCase):
    user_service = UserService()

    def setUp(self):
        self.factory = APIRequestFactory()

        admin_user_data = {
            "username": "admin_test",
            "password": "admin_password",
            "email": "admin_test@gmail.com",
            "role": "admin",
        }

        analyst_user_data = {
            "username": "analyst_test",
            "password": "analyst_password",
            "email": "analyst_test@gmail.com",
            "role": "analyst",
        }

        user_data = {
            "username": "user_test",
            "password": "user_password",
            "email": "user_test@gmail.com",
            "role": "user",
        }

        self.admin = User.objects.create_superuser(**admin_user_data)
        self.admin_jwt_token = self.user_service.authentificate_user(
            self.admin.username, admin_user_data["password"]
        )

        self.analyst = User.objects.create_analyst(**analyst_user_data)
        self.analyst_jwt_token = self.user_service.authentificate_user(
            self.analyst.username, analyst_user_data["password"]
        )

        self.user = User.objects.create_user(**user_data)
        self.user_jwt_token = self.user_service.authentificate_user(
            self.user.username, user_data["password"]
        )

        self.stock = Stock.objects.create(
            name="test Stock 1", symbol="tFS1", price_per_unit_sail=120, price_per_unit_buy=110
        )


class OrderListTestCase(BaseOrderTestCase):
    view = OrderList.as_view()

    def test_order_list_view_access_by_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_list_view_access_by_analyst(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.analyst_jwt_token)
        response = client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_list_view_access_by_user(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserOrderListTestCase(BaseOrderTestCase):
    view = UserOrderList.as_view()

    def test_user_order_list_view_access_by_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        user_id = self.user.id
        response = client.get(reverse("user-order-list", kwargs={"user_id": user_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_order_list_view_access_by_analyst(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.analyst_jwt_token)
        user_id = self.user.id
        response = client.get(reverse("user-order-list", kwargs={"user_id": user_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CurrentUserOrderListTestCase(BaseOrderTestCase):
    view = CurrentUserOrderList.as_view()

    def test_current_user_order_list_access(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.get(reverse("current-user-order-list"))
        self.assertEqual(response.status_code, 200)


class CancelOrderViewTestCase(BaseOrderTestCase):
    view = CancelOrderView.as_view()
    order_service = OrderService()

    def setUp(self):
        super().setUp()

        self.closed_order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": True,
            "status": Order.ORDER_STATUS.CLOSED,
            "user_action_type": "buy",
        }

        self.open_order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": False,
            "user_action_type": Order.USER_ACTION_TYPE.BUY,
            "price_limit": 100,
            "order_type": Order.ORDER_TYPE.LONG,
        }

    def test_cancel_opened_order_admin(self):
        order_opened = Order.objects.create(**self.open_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)

        order_id = order_opened.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(obj_id=order_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.ORDER_STATUS.CANCELED)

    def test_cancel_closed_order_admin(self):
        order_closed = Order.objects.create(**self.closed_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        order_id = order_closed.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(obj_id=order_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)

    def test_cancel_opened_order_user(self):
        order_opened = Order.objects.create(**self.open_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        order_id = order_opened.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(obj_id=order_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.ORDER_STATUS.CANCELED)

    def test_cancel_closed_order_user(self):
        order_closed = Order.objects.create(**self.closed_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        order_id = order_closed.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(obj_id=order_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)


class CreateOrderViewTestCase(BaseOrderTestCase):
    view = CreateOrderView.as_view()
    order_service = OrderService()
    stock_service = StockService()

    def setUp(self):
        super().setUp()

        self.manual_order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": True,
            "user_action_type": "buy",
        }
        self.auto_order_long_buy_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": False,
            "user_action_type": Order.USER_ACTION_TYPE.BUY,
            "price_limit": 100,
            "order_type": Order.ORDER_TYPE.LONG,
        }

        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_create_manual_order_insufficient_balance(self):
        start_balance = 0
        self.user_service.set_new_balance(self.user.id, start_balance)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(
            "http://localhost:8000/api/orders/create/", data=self.manual_order_data
        )

        response_data = response.json()

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(start_balance, end_balance)
        # stock quantity check
        self.assertEqual(response_data.get("detail"), "Order do not create: insufficient balance.")
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_create_manual_order_insufficient_balance_quantity(self):
        start_balance = 200
        self.user_service.set_new_balance(self.user.id, start_balance)

        manual_order_data = dict(self.manual_order_data)
        manual_order_data["quantity"] = 10

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post("http://localhost:8000/api/orders/create/", data=manual_order_data)

        response_data = response.json()

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(start_balance, end_balance)
        # stock quantity check
        self.assertEqual(response_data.get("detail"), "Order do not create: insufficient balance.")
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_create_manual_order_enought_balance(self):
        start_balance = 200
        self.user_service.set_new_balance(self.user.id, start_balance)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(
            "http://localhost:8000/api/orders/create/", data=self.manual_order_data
        )

        response_data = response.json()
        order = response_data.get("order")
        order_status = order.get("status")
        order_closing_price = order.get("closing_price")

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(order_closing_price, (start_balance - end_balance))
        # stock quantity check
        self.assertEqual(order_status, Order.ORDER_STATUS.CLOSED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_auto_order_canceled(self):
        # Проверка условия для долгой продажи, ждем пока цена упадет
        self.stock_service.update(self.stock.id, price_per_unit_sail=120)

        start_balance = 1000
        self.user_service.set_new_balance(self.user.id, start_balance)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(
            "http://localhost:8000/api/orders/create/", data=self.auto_order_long_buy_data
        )

        response_data = response.json()
        order = response_data.get("order")
        order_id = order.get("id")
        order = self.order_service.get_by_id(obj_id=order_id)

        mid_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(start_balance, mid_balance)
        # stock quantity check
        self.assertEqual(order.status, Order.ORDER_STATUS.OPEN)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        not_enough_balance = 10
        self.user_service.set_new_balance(self.user.id, not_enough_balance)
        self.stock_service.update(self.stock.id, price_per_unit_sail=80)

        task = check_open_orders.apply()
        task.get()
        self.assertEqual(task.state, "SUCCESS")

        order = self.order_service.get_by_id(obj_id=order_id)
        order_status_after_cancel = order.status

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(not_enough_balance, end_balance)
        self.assertEqual(order_status_after_cancel, Order.ORDER_STATUS.CANCELED)

    def test_create_auto_order_closed(self):
        # Проверка условия для долгой продажи, ждем пока цена упадет

        self.stock_service.update(self.stock.id, price_per_unit_sail=120)

        start_balance = 1000
        self.user_service.set_new_balance(self.user.id, start_balance)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(
            "http://localhost:8000/api/orders/create/", data=self.auto_order_long_buy_data
        )

        response_data = response.json()
        order = response_data.get("order")
        order_id = order.get("id")
        order = self.order_service.get_by_id(obj_id=order_id)

        mid_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(start_balance, mid_balance)
        # stock quantity check
        self.assertEqual(order.status, Order.ORDER_STATUS.OPEN)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.stock.price_per_unit_sail = 80
        self.stock.save()
        order = self.order_service.get_by_id(obj_id=order_id)

        task = check_open_orders.apply()
        task.get()
        self.assertEqual(task.state, "SUCCESS")

        order = self.order_service.get_by_id(obj_id=order_id)
        # order.refresh_from_db()
        # order.refresh_from_db() return None????

        order_closing_price = order.closing_price
        order_status_after_close = order.status

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(order_closing_price, (start_balance - end_balance))
        self.assertEqual(order_status_after_close, Order.ORDER_STATUS.CLOSED)
