from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views
from rest_framework.response import Response

from .authentication import JWTAuthentication
from .serializers import ObtainTokenSerializer

User = get_user_model()


class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_email = serializer.validated_data.get("username_or_email")
        password = serializer.validated_data.get("password")

        user = User.objects.filter(username=username_or_email).first()
        if user is None:
            user = User.objects.filter(email=username_or_email).first()

        if user is None or not user.check_password(password):
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        jwt_token = JWTAuthentication.create_jwt(user)

        return Response({"token": jwt_token})
