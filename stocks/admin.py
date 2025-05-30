from django.contrib import admin

from .models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "price_per_unit_sail", "price_per_unit_buy")
    list_display_links = ("name",)
