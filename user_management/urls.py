from django.urls import path

from user_management.views import (BalanceView, BlockUserView, ChangeBalanceView, ObtainTokenView,
                                   ResetPasswordView, SubscribeToStockView, SubscriptionsView,
                                   UnlockUserView, UserRegistrationView, UsersView)

urlpatterns = [
    path("token/", ObtainTokenView.as_view(), name="token-obtain"),
    path("register/", UserRegistrationView.as_view(), name="user-registeration"),
    path("user/balance/", BalanceView.as_view(), name="my-balance"),
    path("user/reset_password/", ResetPasswordView.as_view(), name="reset-password"),
    path("user/subscriptions/", SubscriptionsView.as_view(), name="subscriptions-list"),
    path(
        "user/subscribe_to_stock/<int:pk>",
        SubscribeToStockView.as_view(),
        name="subscriptions-list",
    ),
    path("admin/users/", UsersView.as_view(), name="users-list"),
    path("admin/change_balance/user/<int:pk>", ChangeBalanceView.as_view(), name="change-balance"),
    path("admin/user/block/<int:pk>", BlockUserView.as_view(), name="block-user"),
    path("admin/user/unlock/<int:pk>", UnlockUserView.as_view(), name="unlock-user"),
]
