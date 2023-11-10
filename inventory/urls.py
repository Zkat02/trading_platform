from django.urls import path

from .views import InventoryView

urlpatterns = [
    path("user/", InventoryView.as_view(), name="user-inventory"),
]
