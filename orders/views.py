from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import CreateOrderSerializer, OrderSerializer
from orders.services import OrderService
from user_management.permissions import CanCancelOrder, IsAdminOrAnalyst, IsUser, IsUserOrAdmin

order_service = OrderService()


class OrderList(ListAPIView):
    """
    Get list of all orders.
    Allow only for admin or analyst
    """

    permission_classes = [IsAdminOrAnalyst]
    queryset = order_service.get_all()
    serializer_class = OrderSerializer


class UserOrderList(ListAPIView):
    """
    Get list of user orders by his id.
    Allow only for admin or analyst
    """

    permission_classes = [IsAdminOrAnalyst]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return order_service.filter_orders(user=user_id)


class CurrentUserOrderList(ListAPIView):
    """
    Get list of current user's orders.
    Allow only for user
    """

    permission_classes = [IsUser]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return order_service.filter_orders(user=self.request.user)


class CancelOrderView(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CanCancelOrder]

    def perform_update(self, serializer):
        if serializer.instance.status == "open":
            serializer.instance.status = "canceled"
            serializer.instance.save()


class CreateOrderView(APIView):
    """
    User buy stock by price price_per_unit_sail.

    User can create order only for himself.
    Admin can create order for all users by his user_id followed in parametrs in body.
    """

    serializer_class = CreateOrderSerializer
    permission_classes = [IsUserOrAdmin]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        message = order_service.create_order(**serializer.data)
        return Response(
            {
                "message": message,
            },
            status=status.HTTP_201_CREATED,
        )
