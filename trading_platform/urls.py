from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user_management/", include("user_management.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/inventory/", include("inventory.urls")),
    path("api/stocks/", include("stocks.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
