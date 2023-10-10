from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user_management/", include("user_management.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/subscriptions/", include("inventory.urls")),
]
