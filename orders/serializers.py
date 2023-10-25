from django.contrib.auth import get_user_model
from rest_framework import serializers

from stocks.models import Stock

from .models import Order

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class CreateOrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, default=serializers.CurrentUserDefault()
    )
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all(), required=True)
    manual = serializers.BooleanField(default=True)

    class Meta:
        model = Order
        fields = (
            "stock",
            "quantity",
            "order_type",
            "user_action_type",
            "price_limit",
            "user",
            "manual",
        )

    def validate_user(self, user):
        if user.role == "user" and user != self.context["request"].user:
            raise serializers.ValidationError(
                "You can only create an order for yourself as a 'user' role."
            )
        return user

    def validate_manual(self, manual):
        if not manual:
            if "order_type" not in self.initial_data or "price_limit" not in self.initial_data:
                raise serializers.ValidationError(
                    'Both "order_type" and "price_limit" are required when field "manual" is False.'
                )
        return manual
