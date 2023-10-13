from django.urls import path

from user_management.veiws import ObtainTokenView, UserRegistrationView

urlpatterns = [
    path("token/", ObtainTokenView.as_view(), name="token_obtain_pair"),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
]
