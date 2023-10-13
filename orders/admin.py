from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "stock", "quantity", "order_type", "price_limit", "status", "manual")
    list_display_links = ("user", "stock")
    list_filter = ("user", "stock", "order_type", "status", "manual")
