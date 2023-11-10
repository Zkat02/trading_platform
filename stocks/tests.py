from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from stocks.models import Stock
from stocks.services import StockService
from user_management.services import UserService

User = get_user_model()


class BaseStockTestCase(TestCase):
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


class StockViewTests(BaseStockTestCase):
    def test_get_stocks_allowedAny(self):
        client = APIClient()
        response = client.get(reverse("all-stocks"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_stock_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)

        stock_data = {
            "name": "test Stock 2",
            "symbol": "tFS1",
            "price_per_unit_sail": 110,
            "price_per_unit_buy": 70,
            "available_quantity": 10,
        }

        response = client.post(reverse("all-stocks"), data=stock_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StockDetailViewTests(BaseStockTestCase):
    def test_get_stock_detail_allowedAny(self):
        client = APIClient()
        response = client.get(reverse("stock-detail", kwargs={"pk": 1}))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_update_stock_not_allowedAny(self):
        client = APIClient()

        stock_data = {
            "name": "test Stock 3",
            "symbol": "tFS1",
            "price_per_unit_sail": 110,
            "price_per_unit_buy": 70,
            "available_quantity": 10,
        }
        stock = Stock.objects.create(**stock_data)
        update_data = {"name": "Updated Stock"}

        response = client.put(reverse("stock-detail", kwargs={"pk": stock.id}), data=update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stock_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)

        stock_data = {
            "name": "test Stock 4",
            "symbol": "tFS1",
            "price_per_unit_sail": 110,
            "price_per_unit_buy": 70,
            "available_quantity": 10,
        }
        stock = Stock.objects.create(**stock_data)
        update_data = {"name": "Updated Stock"}

        response = client.put(reverse("stock-detail", kwargs={"pk": stock.id}), data=update_data)

        stock.refresh_from_db()
        self.assertEqual(stock.name, "Updated Stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_stock_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_jwt_token)

        stock_data = {
            "name": "test Stock 5",
            "symbol": "tFS1",
            "price_per_unit_sail": 110,
            "price_per_unit_buy": 70,
            "available_quantity": 10,
        }
        stock = Stock.objects.create(**stock_data)

        response = client.delete(reverse("stock-detail", kwargs={"pk": stock.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
