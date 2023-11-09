from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import OrderService
from orders.tasks import check_open_orders
from orders.views import (
    CancelOrderView,
    CreateOrderView,
    CurrentUserOrderList,
    OrderList,
    UserOrderList,
)
from stocks.models import Stock
from stocks.serializers import StockSerializer
from stocks.services import StockService
from trading_platform.celery import app as celery_app
from user_management.services import UserService

User = get_user_model()


class BaseUserTestCase(TestCase):
    stock_service = StockService()
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
            name="test Stock 1", symbol="tFS1", price_per_unit_sail=120, price_per_unit_buy=110
        )


class ObtainTokenViewTestCase(BaseUserTestCase):
    def test_obtain_token(self):
        client = APIClient()

        data = {
            "username": "user_test",
            "password": "user_password",
        }

        response = client.post(reverse("token-obtain"), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data
        self.assertIn("token", response_data)
        self.user_jwt_token = response_data.get("token")


class UserRegistrationViewTestCase(BaseUserTestCase):
    def test_register_user(self):
        data = {
            "username": "user_test2",
            "password": "user_password2",
            "email": "user_test3@gmail.com",
            "role": "user",
        }

        client = APIClient()
        response = client.post(reverse("user-registeration"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertIn("token", response_data)


class ResetPasswordViewTestCase(BaseUserTestCase):
    def test_reset_pass(self):
        data = {
            "username": "user_test",
            "old_password": "user_password",
            "new_password": "user_password2",
            "confirm_new_password": "user_password2",
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.post(reverse("reset-password"), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data
        self.assertIn("new_token", response_data)
        self.user_jwt_token = response_data.get("new_token")


class UsersViewTestCase(BaseUserTestCase):
    def test_get_list_users_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.get(reverse("users-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        self.assertIn("users", response_data)


class BlockUserViewTestCase(BaseUserTestCase):
    def test_block_user_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.patch(reverse("block-user", kwargs={"pk": self.user.id}))
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.is_active, False)

    def test_block_user_analyst(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.analyst_jwt_token)
        response = client.patch(reverse("block-user", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnblockUserViewTestCase(BaseUserTestCase):
    def test_unblock_user_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        self.user.is_active = False
        self.user.save()
        response = client.patch(reverse("unlock-user", kwargs={"pk": self.user.id}))
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.is_active, True)

    def test_unblock_user_analyst(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.analyst_jwt_token)
        response = client.patch(reverse("unlock-user", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BalanceViewTestCase(BaseUserTestCase):
    def test_balance_user(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        response = client.get(reverse("my-balance"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("balance", response.data)
        self.assertEqual(self.user.balance, response.data.get("balance"))

    def test_balance_analyst(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.analyst_jwt_token)
        response = client.get(reverse("my-balance"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("balance", response.data)
        self.assertEqual(self.analyst.balance, response.data.get("balance"))

    def test_balance_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.get(reverse("my-balance"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("balance", response.data)
        self.assertEqual(self.admin.balance, response.data.get("balance"))


class ChangeBalanceViewTestCase(BaseUserTestCase):
    def test_admin_get_users_balance(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.get(reverse("change-balance", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("balance", response.data)

    def test_change_users_balance_new_balance(self):
        new_balance = 50.00
        data = {"new_balance": new_balance}

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.post(reverse("change-balance", kwargs={"pk": self.user.id}), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("new_balance", response.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, new_balance)

    def test_change_users_balance_value_to_add(self):
        value_to_add = 50.00
        old_balance = self.user.balance
        data = {"value_to_add": value_to_add}

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)
        response = client.post(reverse("change-balance", kwargs={"pk": self.user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("new_balance", response.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, old_balance + value_to_add)


class SubscriptionsViewTestCase(BaseUserTestCase):

    def test_get_empty_list_of_subscriptions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        response = client.get(reverse("subscriptions-list"))

        list_subs = self.user.subscriptions#self.user.subscriptions if self.user.subscriptions.exists() else []

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("stocks", response.data)
        self.assertEqual(
            StockSerializer(list_subs, many=True).data,
            StockSerializer(response.data.get("stocks"), many=True).data,
        )

    def test_get_not_empty_list_of_subscriptions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        
        stock_id = self.stock.id
        self.stock_service.create_subscription(self.user.id, stock_id)

        response = client.get(reverse("subscriptions-list"))

        self.user.refresh_from_db()
        list_subs = self.user.subscriptions

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("stocks", response.data)
        self.assertEqual(
            StockSerializer(list_subs, many=True).data,
            StockSerializer(response.data.get("stocks"), many=True).data,
        )


class SubscribeToStockViewTestCase(BaseUserTestCase):
    def test_subscribe_to_stock(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        stock_id = self.stock.id

        response = client.post(reverse("subscribe-to-stock", kwargs={"pk": stock_id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Subscribed to the stock successfully.")

    def test_unsubscribe_from_stock(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)
        stock_id = self.stock.id

        stock_id = self.stock.id
        self.stock_service.create_subscription(self.user.id, stock_id)
        self.user.refresh_from_db()

        response = client.delete(reverse("subscribe-to-stock", kwargs={"pk": stock_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Unsubscribed from the stock successfully.")
        
        self.user.refresh_from_db()
        list_subs = self.user.subscriptions
        self.assertEqual(StockSerializer(list_subs, many=True).data,[])