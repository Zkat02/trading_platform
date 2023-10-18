from django.urls import path

from .views import StockDetailView, StockView, SubscribeToStockView

urlpatterns = [
    path("all/", StockView.as_view(), name="all-stocks"),
    path("<int:pk>/", StockDetailView.as_view(), name="stock-detail"),
    path("subscribe/<int:pk>/", SubscribeToStockView.as_view(), name="subscribe-to-stock"),
]
