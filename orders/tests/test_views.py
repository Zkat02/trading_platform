from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from inventory.services import InventoryService
from orders.models import Order
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
            name="test Stock 1",
            symbol="tFS1",
            price_per_unit_sail=120,
            price_per_unit_buy=110,
            available_quantity=10,
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

        order = self.order_service.get_by_id(order_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.ORDER_STATUS.CANCELED)

    def test_cancel_closed_order_admin(self):
        order_closed = Order.objects.create(**self.closed_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        order_id = order_closed.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(order_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)

    def test_cancel_opened_order_user(self):
        order_opened = Order.objects.create(**self.open_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        order_id = order_opened.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(order_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.ORDER_STATUS.CANCELED)

    def test_cancel_closed_order_user(self):
        order_closed = Order.objects.create(**self.closed_order_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        order_id = order_closed.id

        response = client.put(reverse("cancel-order", kwargs={"pk": order_id}))

        order = self.order_service.get_by_id(order_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)


class CreateOrderViewTestCase(BaseOrderTestCase):
    view = CreateOrderView.as_view()
    order_service = OrderService()
    stock_service = StockService()
    inventory_service = InventoryService()

    def setUp(self):
        super().setUp()

        self.manual_buy_order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 1,
            "manual": True,
            "user_action_type": "buy",
        }
        self.manual_sell_order_data = {
            "user_id": self.user.id,
            "stock_id": self.stock.id,
            "quantity": 3,
            "manual": True,
            "user_action_type": "sell",
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

    def test_create_manual_buy_order_insufficient_balance(self):
        start_balance = 0
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(reverse("create-order"), data=self.manual_buy_order_data)

        response_data = response.json()

        self.user.refresh_from_db()
        self.stock.refresh_from_db()

        end_balance = self.user_service.get_user_balance(self.user.id)

        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(start_balance, end_balance)
        self.assertEqual(start_stock_available_quantity, end_stock_available_quantity)
        self.assertEqual(response_data.get("detail"), "Order not create: insufficient balance.")
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_create_manual_buy_order_insufficient_balance_to_buy_big_quantity(self):
        start_balance = 200
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        manual_buy_order_data = dict(self.manual_buy_order_data)
        manual_buy_order_data["quantity"] = 9

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        response = client.post(reverse("create-order"), data=manual_buy_order_data)
        response_data = response.json()

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(start_balance, end_balance)
        self.assertEqual(start_stock_available_quantity, end_stock_available_quantity)
        self.assertEqual(response_data.get("detail"), "Order not create: insufficient balance.")
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_create_manual_buy_order_insufficient_stock_available_quantity(self):
        start_balance = 100000
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        manual_buy_order_data = dict(self.manual_buy_order_data)
        manual_buy_order_data["quantity"] = 20

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        response = client.post(reverse("create-order"), data=manual_buy_order_data)
        response_data = response.json()

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(start_balance, end_balance)
        self.assertEqual(start_stock_available_quantity, end_stock_available_quantity)
        self.assertEqual(
            response_data.get("detail"),
            "Order not created: stock available_quantity not enought for buy.",
        )
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_create_manual_sell_order_insufficient_stock_quantity_in_inventory(self):
        inventory_data = {
            "user": self.user,
            "stock": self.stock,
            "quantity": 1,
        }
        inventory = self.inventory_service.create(**inventory_data)

        start_balance = 100000
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        start_inventory_quantity = inventory.quantity

        manual_sell_order_data = dict(self.manual_sell_order_data)
        manual_sell_order_data["quantity"] = 20

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        response = client.post(reverse("create-order"), data=manual_sell_order_data)
        response_data = response.json()

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        inventory.refresh_from_db()
        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity
        end_inventory_quantity = inventory.quantity

        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(
            response_data.get("detail"),
            "Order not created: you own not enought stock quantity for sell.",
        )
        self.assertEqual(start_balance, end_balance)
        self.assertEqual(start_stock_available_quantity, end_stock_available_quantity)
        self.assertEqual(start_inventory_quantity, end_inventory_quantity)

    def test_create_manual_buy_order_OK(self):
        start_balance = 200
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        start_inventory_quantity = 10
        inventory_data = {
            "user": self.user,
            "stock": self.stock,
            "quantity": start_inventory_quantity,
        }
        inventory = self.inventory_service.create(**inventory_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(reverse("create-order"), data=self.manual_buy_order_data)

        self.assertIn("order", response.data)
        order_id = response.data.get("order").get("id")
        order = self.order_service.get_by_id(order_id)

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)
        self.assertEqual(order.closing_price * order.quantity, (start_balance - end_balance))
        self.assertEqual(
            order.quantity, (start_stock_available_quantity - end_stock_available_quantity)
        )

        inventory.refresh_from_db()
        self.assertEqual(order.quantity, (inventory.quantity - start_inventory_quantity))

    def test_create_manual_sell_order_OK(self):
        start_balance = 200
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        start_inventory_quantity = 10
        inventory_data = {
            "user": self.user,
            "stock": self.stock,
            "quantity": start_inventory_quantity,
        }
        inventory = self.inventory_service.create(**inventory_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(reverse("create-order"), data=self.manual_sell_order_data)

        self.assertIn("order", response.data)
        order_id = response.data.get("order").get("id")
        order = self.order_service.get_by_id(order_id)

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)
        self.assertEqual((start_balance + order.closing_price * order.quantity), end_balance)
        self.assertEqual(
            order.quantity, (end_stock_available_quantity - start_stock_available_quantity)
        )

        inventory.refresh_from_db()
        self.assertEqual(order.quantity, (start_inventory_quantity - inventory.quantity))

    def test_create_auto_long_buy_order_canceled(self):
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

        order.refresh_from_db()
        order_status_after_cancel = order.status

        end_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(not_enough_balance, end_balance)
        self.assertEqual(order_status_after_cancel, Order.ORDER_STATUS.CANCELED)

    def test_create_auto_long_buy_order_OK(self):
        # Проверка условия для долгой продажи, ждем пока цена упадет

        self.stock_service.update(self.stock.id, price_per_unit_sail=120)

        start_balance = 1000
        self.user_service.set_new_balance(self.user.id, start_balance)

        start_stock_available_quantity = self.stock.available_quantity

        start_inventory_quantity = 10
        inventory_data = {
            "user": self.user,
            "stock": self.stock,
            "quantity": start_inventory_quantity,
        }
        inventory = self.inventory_service.create(**inventory_data)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(
            "http://localhost:8000/api/orders/create/", data=self.auto_order_long_buy_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order", response.data)
        response_data = response.json()
        order_id = response_data.get("order").get("id")
        order = self.order_service.get_by_id(obj_id=order_id)

        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        mid_balance = self.user_service.get_user_balance(self.user.id)

        self.assertEqual(order.status, Order.ORDER_STATUS.OPEN)
        self.assertEqual(start_balance, mid_balance)
        self.assertEqual(start_stock_available_quantity, self.stock.available_quantity)

        self.stock.price_per_unit_sail = 80
        self.stock.save()

        order.refresh_from_db()
        task = check_open_orders.apply()
        task.get()
        self.assertEqual(task.state, "SUCCESS")

        order.refresh_from_db()
        self.user.refresh_from_db()
        self.stock.refresh_from_db()
        inventory.refresh_from_db()

        end_balance = self.user_service.get_user_balance(self.user.id)
        end_stock_available_quantity = self.stock.available_quantity

        self.assertEqual(order.closing_price, (start_balance - end_balance))
        self.assertEqual(order.status, Order.ORDER_STATUS.CLOSED)
        self.assertEqual(
            order.quantity, (start_stock_available_quantity - end_stock_available_quantity)
        )
        self.assertEqual(order.quantity, (inventory.quantity - start_inventory_quantity))
