from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from stocks.models import Stock
from stocks.serializers import StockSerializer
from user_management.permissions import IsAdmin, IsAuthenticated, IsUser

from .authentication import JWTAuthentication
from .serializers import (ChangeBalanceSerializer, ObtainTokenSerializer, ResetPasswordSerializer,
                          UserSerializer)

User = get_user_model()


class ObtainTokenView(APIView):
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


class UserRegistrationView(APIView):
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


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")

        try:
            user = User.objects.get(username=username)

            if not user.check_password(old_password):
                return Response(
                    {"error_message": "Old password isn't correct."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            jwt_token = JWTAuthentication.create_jwt(user)

            return Response(
                {"message": "New password was installed successfully.", "your_JWT_token": jwt_token}
            )
        except User.DoesNotExist:
            return Response({"error_message": f"User with username - {username} dont't exist"})


class UsersView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response({"users": serializer.data})


class BlockUserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)


class UnlockUserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response({"message": "User unlocked successfully."}, status=status.HTTP_200_OK)


class BalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        balance = request.user.balance
        return Response({"balance": balance})


class ChangeBalanceView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = ChangeBalanceSerializer

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            return Response({"balance": user.balance})
        except User.DoesNotExist:
            return Response(
                {"error_message": "user doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_balance = serializer.validated_data.get("new_balance")
            value_to_add = serializer.validated_data.get("value_to_add")

            if new_balance is not None:
                try:
                    user = User.objects.get(pk=pk)
                    user.balance = new_balance
                    user.save()
                    return Response(
                        {
                            "message": "Balance was changed successfully.",
                            "new_balance": user.balance,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except User.DoesNotExist:
                    return Response(
                        {"error_message": "User doesn't exist"}, status=status.HTTP_404_NOT_FOUND
                    )

            if value_to_add is not None:
                try:
                    user = User.objects.get(pk=pk)
                    user.balance += value_to_add
                    user.save()
                    return Response(
                        {
                            "message": "Balance was increased successfully.",
                            "new_balance": user.balance,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except User.DoesNotExist:
                    return Response(
                        {"error_message": "User doesn't exist"}, status=status.HTTP_404_NOT_FOUND
                    )

            return Response(
                {"error_message": "new_balance or value_to_add not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(APIView):
    permission_classes = [IsUser]

    def get(self, request):
        stocks = request.user.subscriptions.all()
        serializer = StockSerializer(stocks, many=True)
        return Response({"message": "List of stocks you subscribed.", "stocks": serializer.data})


class SubscribeToStockView(APIView):
    permission_classes = [IsUser]

    def get(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            serializer = StockSerializer(stock)
            if request.user.subscriptions.filter(pk=pk).exists():
                return Response(
                    {"messege": "You subscribe to this stock.", "stock": serializer.data}
                )
            return Response(
                {"messege": "You have not subscribed to this stock yet.", "stock": serializer.data}
            )
        except Stock.DoesNotExist:
            return Response({"error_message": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            if request.user.subscriptions.filter(pk=pk).exists():
                return Response(
                    {"error_message": "You are already subscribed to this stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.subscriptions.add(stock)
            return Response({"message": "Subscribed to the stock successfully"})
        except Stock.DoesNotExist:
            return Response({"error_message": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            if request.user.subscriptions.filter(pk=pk).exists():
                request.user.subscriptions.remove(stock)
                return Response({"message": "Unsubscribed from the stock successfully"})

            return Response(
                {"error_message": "You are not subscribed to this stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Stock.DoesNotExist:
            return Response({"error_message": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
