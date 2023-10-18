from django.urls import path

from user_management.views import (GetBalanceView, ObtainTokenView, SubscriptionsView,
                                   UserRegistrationView, UsersView)

urlpatterns = [
    path("token/", ObtainTokenView.as_view(), name="token_obtain_pair"),
    path("register/", UserRegistrationView.as_view(), name="user_registeration"),
    path("get_balance/", GetBalanceView.as_view(), name="get_balance"),
    path("subscriptions/<int:pk>", SubscriptionsView.as_view(), name="subscriptions-list"),
    path("users/", UsersView.as_view(), name="users-list"),
]
