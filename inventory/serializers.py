from rest_framework import serializers

from inventory.models import Inventory
from stocks.serializers import StockSerializer


class InventorySerializer(serializers.ModelSerializer):
    stock = StockSerializer()

    class Meta:
        model = Inventory

        fields = (
            "stock",
            "user",
            "quantity",
        )
