from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views
from rest_framework.response import Response

from user_management.models import CustomUser

from .authentication import JWTAuthentication
from .serializers import ObtainTokenSerializer, UserSerializer

User = get_user_model()


class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        try:
            user = User.objects.get(username=username)

            if user is None or not user.check_password(password):
                return Response(
                    {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )

            jwt_token = JWTAuthentication.create_jwt(user)

            return Response({"token": jwt_token})
        except User.DoesNotExist:
            return Response({"error_message": f"User with username - {username} dont't exist"})


class UserRegistrationView(views.APIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()
            jwt_token = JWTAuthentication.create_jwt(user)
            return Response(
                {
                    "message": "User registered successfully.",
                    "token": jwt_token,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetBalanceView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        balance = request.user.balance
        return Response({"balance": balance})
