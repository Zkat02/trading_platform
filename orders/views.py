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
    Retrieve a list of all orders.
    Allowed only for admin or analyst.
    """

    permission_classes = [IsAdminOrAnalyst]
    queryset = order_service.get_all()
    serializer_class = OrderSerializer


class UserOrderList(ListAPIView):
    """
    Retrieve a list of orders for a specific user by their ID.
    Allowed only for admin or analyst.
    """

    permission_classes = [IsAdminOrAnalyst]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return order_service.filter_objs(user=user_id)


class CurrentUserOrderList(ListAPIView):
    """
    Retrieve a list of orders for the current user.
    Allowed only for the user.
    """

    permission_classes = [IsUser]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return order_service.filter_objs(user=self.request.user)


class CancelOrderView(RetrieveAPIView):
    """
    Retrieve an order and if status is open, cancel it.

    Allowed only for user created this order.
    """

    serializer_class = OrderSerializer
    permission_classes = [CanCancelOrder]

    def put(self, request, pk):
        order = order_service.get_by_id(obj_id=pk)
        if order_service.can_cancel_order(order=order):
            order_service.cancel_order(order=order)
            return Response(
                {
                    "message": "Order canceled successfully",
                    "order": self.serializer_class(order).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Order cannot be canceled", "order": self.serializer_class(order).data},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateOrderView(APIView):
    """
    Create a new order for buying stocks.

    Users can create orders for themselves. Admins can create orders for any user by providing the user_id in the request body.
    """

    serializer_class = CreateOrderSerializer
    permission_classes = [IsUserOrAdmin]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = order_service.create_order(**serializer.data)

        if order.status == Order.ORDER_STATUS.CLOSED:
            message = f"Order closed successfully. Closing price {order.closing_price}."
        if order.status == Order.ORDER_STATUS.OPEN:
            message = "We notice you by mail when order will be closed."

        return Response(
            {"message": message, "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED,
        )
