from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from stocks.serializers import StockSerializer
from stocks.services import StockService
from user_management.exceptions import DoNotBlockException, DoNotUnlockException
from user_management.permissions import IsAdmin, IsAuthenticated, IsUser
from user_management.serializers import (ChangeBalanceSerializer, ObtainTokenSerializer,
                                         ResetPasswordSerializer, UserSerializer)
from user_management.services import UserService

User = get_user_model()


user_service = UserService()
stock_service = StockService()


class ObtainTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer = ObtainTokenSerializer

    def post(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt_token = user_service.authentificate_user(**serializer.validated_data)
        return Response({"token": jwt_token})


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer = UserSerializer

    def post(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_service.register_user(**serializer.validated_data)
        jwt_token = user_service.authentificate_user(
            username=user.username, password=serializer.validated_data.get("password")
        )
        return Response(
            {
                "message": "User registered successfully.",
                "token": jwt_token,
            },
            status=status.HTTP_201_CREATED,
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_service.reset_password(**serializer.validated_data)
        jwt_token = user_service.authentificate_user(
            username=user.username, password=serializer.validated_data.get("new_password")
        )

        return Response(
            {"message": "New password was installed successfully.", "your_JWT_token": jwt_token}
        )


class UsersView(APIView):
    permission_classes = [IsAdmin]
    serializer = UserSerializer

    def get(self, request):  # pylint: disable=unused-argument
        users = user_service.get_all_users()
        users = self.serializer(users, many=True).data
        return Response({"users": users})


class BlockUserView(RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        if user_service.block_user(user_id=kwargs.get("pk")):
            return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)
        raise DoNotBlockException()


class UnlockUserView(RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        if user_service.unlock_user(user_id=kwargs.get("pk")):
            return Response({"message": "User unlocked successfully."}, status=status.HTTP_200_OK)
        raise DoNotUnlockException()


class BalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        balance = user_service.get_user_balance(user_id=request.user.id)
        return Response({"balance": balance})


class ChangeBalanceView(APIView):
    permission_classes = [IsAdmin]
    serializer = ChangeBalanceSerializer

    def get(self, request, pk):  # pylint: disable=unused-argument
        balance = user_service.get_user_balance(user_id=pk)
        return Response({"balance": balance})

    def post(self, request, pk):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message, balance = user_service.change_balance(user_id=pk, **serializer.validated_data)
        return Response(
            {
                "message": message,
                "new_balance": balance,
            },
            status=status.HTTP_201_CREATED,
        )


class SubscriptionsView(APIView):
    permission_classes = [IsUser]

    def get(self, request):
        user_subscribed_stocks = stock_service.get_all_user_subscriptions(user_id=request.user.id)
        return Response(
            {
                "message": "List of stocks you subscribed.",
                "stocks": StockSerializer(user_subscribed_stocks, many=True).data,
            }
        )


class SubscribeToStockView(APIView):
    permission_classes = [IsUser]

    def get(self, request, pk):
        stock = stock_service.get_by_id(pk)
        message = stock_service.check_subscription_message(user_id=request.user.id, stock_id=pk)
        return Response({"message": message, "stock": StockSerializer(stock).data})

    def post(self, request, pk):
        stock_service.create_subscription(user_id=request.user.id, stock_id=pk)
        return Response(
            {"message": "Subscribed to the stock successfully"}, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        stock_service.remove_subscription(user_id=request.user.id, stock_id=pk)
        return Response({"message": "Unsubscribed from the stock successfully."})
