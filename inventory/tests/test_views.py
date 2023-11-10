from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from inventory.serializers import InventorySerializer
from inventory.services import InventoryService
from stocks.models import Stock
from user_management.services import UserService

User = get_user_model()


class InventoryViewTestCase(TestCase):
    user_service = UserService()
    inventory_service = InventoryService()

    def setUp(self):
        user_data = {
            "username": "user_test",
            "password": "user_password",
            "email": "user_test@gmail.com",
            "role": "user",
            "balance": 100,
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

    def test_get_user_inventory(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_jwt_token)

        inventory_data = {
            "user": self.user,
            "stock": self.stock,
            "quantity": 1,
        }
        inventory = self.inventory_service.create(**inventory_data)

        response = client.get(reverse("user-inventory"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("inventory", response.data)

        serialized_inventory = InventorySerializer(inventory).data
        response_inventory = response.json()["inventory"]
        self.assertEqual(response_inventory, [serialized_inventory])
