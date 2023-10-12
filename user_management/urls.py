from django.urls import path

from user_management.veiws import ObtainTokenView

urlpatterns = [
    path("token/", ObtainTokenView.as_view(), name="token_obtain_pair"),
]
