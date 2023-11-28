from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "stock", "quantity")
    list_display_links = ("user", "stock")
    list_filter = ("user", "stock")
