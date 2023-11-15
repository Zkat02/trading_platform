from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from stocks.serializers import StockSerializer
from stocks.services import StockService
from user_management.permissions import IsAdmin, IsAuthenticated, IsUser
from user_management.serializers import (ChangeBalanceSerializer, ObtainTokenSerializer,
                                         ResetPasswordSerializer, UserSerializer)
from user_management.services import UserService

User = get_user_model()

user_service = UserService()
stock_service = StockService()


class ObtainTokenView(APIView):
    """
    Obtain JWT token by user authentication.
    """
    permission_classes = [permissions.AllowAny]
    serializer = ObtainTokenSerializer

    def post(self, request):
        """
        Authenticate user and provide JWT token.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response containing the JWT token.
        """
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt_token = user_service.authentificate_user(**serializer.validated_data)
        return Response({"token": jwt_token})


class UserRegistrationView(APIView):
    """
    Register new user.
    """
    permission_classes = [permissions.AllowAny]
    serializer = UserSerializer

    def post(self, request):
        """
        Register a new user and provide JWT token upon successful registration.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response containing the registered user information and JWT token.
        """
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
    """
    Reset user password.
    """
    permission_classes = [IsAuthenticated]
    serializer = ResetPasswordSerializer

    def post(self, request):
        """
        Reset the user's password and provide a new JWT token.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response confirming successful password change.
        """
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_service.reset_password(**serializer.validated_data)
        jwt_token = user_service.authentificate_user(
            username=user.username, password=serializer.validated_data.get("new_password")
        )

        return Response(
            {"message": "New password was installed successfully.",
              "new_token": jwt_token}
        )


class UsersView(APIView):
    """
    List all users.
    """
    permission_classes = [IsAdmin]
    serializer = UserSerializer

    def get(self, request):  # pylint: disable=unused-argument
        """
        Get a list of all users.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response containing a list of users.
        """
        users = user_service.get_all()
        users = self.serializer(users, many=True).data
        return Response({"users": users})


class BlockUserView(RetrieveUpdateAPIView):
    """
    Block a user.
    """
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Block a user by user ID.

        Args:
        - request: HTTP Request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: JSON response confirming the successful blocking of the user.
        """
        user_service.block_user(user_id=kwargs.get("pk"))
        return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)


class UnblockUserView(RetrieveUpdateAPIView):
    """
    Unblock a user.
    """
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Unblock a user by user ID.

        Args:
        - request: HTTP Request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: JSON response confirming the successful unblocking of the user.
        """
        user_service.unblock_user(user_id=kwargs.get("pk"))
        return Response({"message": "User unblocked successfully."}, status=status.HTTP_200_OK)


class BalanceView(APIView):
    """
    Retrieve user balance.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):  # pylint: disable=unused-argument
        """
        Get the balance of the authenticated user.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response containing the user's balance.
        """
        balance = user_service.get_user_balance(user_id=request.user.id)
        return Response({"balance": balance})


class ChangeBalanceView(APIView):
    """
    Change user balance.
    """
    permission_classes = [IsAdmin]
    serializer = ChangeBalanceSerializer

    def get(self, request, pk):  # pylint: disable=unused-argument
        """
        Get the balance of the specified user.

        Args:
        - request: HTTP Request object.
        - pk: User ID.

        Returns:
        - Response: JSON response containing the balance of the specified user.
        """
        balance = user_service.get_user_balance(user_id=pk)
        return Response({"balance": balance})

    def post(self, request, pk):
        """
        Change the balance of the specified user.

        Args:
        - request: HTTP Request object.
        - pk: User ID.

        Returns:
        - Response: JSON response confirming the successful change in user balance.
        """
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_balance = user_service.change_balance(user_id=pk, **serializer.validated_data)
        return Response(
            {
                "message": "Balance was updated successfully.",
                "new_balance": new_balance,
            },
            status=status.HTTP_200_OK,
        )


class SubscriptionsView(APIView):
    """
    Retrieve user subscriptions.
    """
    permission_classes = [IsUser]

    def get(self, request):
        """
        Get the list of stocks that the user is subscribed to.

        Args:
        - request: HTTP Request object.

        Returns:
        - Response: JSON response containing the list of user-subscribed stocks.
        """
        user_subscribed_stocks = stock_service.get_all_user_subscriptions(user_id=request.user.id)
        return Response(
            {
                "message": "List of stocks you subscribed.",
                "stocks": StockSerializer(user_subscribed_stocks, many=True).data,
            }
        )


class SubscribeToStockView(APIView):
    """
    Subscribe to and unsubscribe from a stock.
    """
    permission_classes = [IsUser]

    def get(self, request, pk):
        """
        Check if the user is subscribed to a stock.

        Args:
        - request: HTTP Request object.
        - pk: Stock ID.

        Returns:
        - Response: JSON response indicating the subscription status for the stock.
        """
        stock = stock_service.get_by_id(pk)
        subscribed = stock_service.check_subscription(user_id=request.user.id, stock_id=pk)
        if subscribed:
            message = "You are subscribed to this stock."
        else:
            message = "You have not subscribed to this stock yet."

        return Response({"message": message, "stock": StockSerializer(stock).data})

    def post(self, request, pk):
        """
        Subscribe to a stock.

        Args:
        - request: HTTP Request object.
        - pk: Stock ID.

        Returns:
        - Response: JSON response confirming successful subscription to the stock.
        """
        stock_service.create_subscription(user_id=request.user.id, stock_id=pk)
        return Response(
            {"message": "Subscribed to the stock successfully."}, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        """
        Unsubscribe from a stock.

        Args:
        - request: HTTP Request object.
        - pk: Stock ID.

        Returns:
        - Response: JSON response confirming successful unsubscription from the stock.
        """
        stock_service.remove_subscription(user_id=request.user.id, stock_id=pk)
        return Response({"message": "Unsubscribed from the stock successfully."})
