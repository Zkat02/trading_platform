from django.urls import path

from .views import CancelOrderView, CreateOrderView, CurrentUserOrderList, OrderList, UserOrderList

urlpatterns = [
    path("list/", OrderList.as_view(), name="order-list"),
    path("list/user/<int:user_id>/", UserOrderList.as_view(), name="user-order-list"),
    path("list/user/current/", CurrentUserOrderList.as_view(), name="current-user-order-list"),
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("cancel/<int:pk>", CancelOrderView.as_view(), name="cancel-order"),
]
