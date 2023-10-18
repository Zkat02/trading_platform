from rest_framework import serializers

from user_management.models import CustomUser


class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "password", "email", "role")
