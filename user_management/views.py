from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views
from rest_framework.response import Response

from stocks.models import Stock
from stocks.serializers import StockSerializer
from user_management.models import CustomUser
from user_management.permissions import IsUser

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


class UsersView(views.APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"users": serializer.data})


class GetBalanceView(views.APIView):
    permission_classes = [IsUser]

    def get(self, request):
        balance = request.user.balance
        return Response({"balance": balance})


class SubscriptionsView(views.APIView):
    permission_classes = [IsUser]

    def get(self, request):
        stocks = Stock.objects.filter(user=request.user)
        serializer = StockSerializer(stocks, many=True)
        return Response({"stocks": serializer.data})

    def delete(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            if stock.user == request.user:
                stock.user.remove(request.user)
                return Response({"message": "Unsubscribed from the stock successfully"})
            else:
                return Response(
                    {"error_message": "You are not subscribed to this stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Stock.DoesNotExist:
            return Response({"error_message": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
