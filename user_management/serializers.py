from rest_framework import serializers


class ObtainTokenSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField()
