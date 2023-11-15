from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user_management.models import CustomUser


class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError("new_password and confirm_new_password do not match.")

        return data


class UserSerializer(serializers.ModelSerializer):
    blocked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "password", "email", "role", "blocked")

    def get_blocked(self, obj):
        return not obj.is_active


class ChangeBalanceSerializer(serializers.Serializer):
    new_balance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    value_to_add = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate(self, data):
        new_balance = data.get("new_balance")
        value_to_add = data.get("value_to_add")

        if not new_balance and not value_to_add:
            raise ValidationError(
                "You must provide either 'new_balance' or 'value_to_add' but not both."
            )
        if new_balance and value_to_add:
            raise ValidationError(
                "You can provide either 'new_balance' or 'value_to_add', but not both."
            )

        return data
