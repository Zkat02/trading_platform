from django.db import models

from stocks.models import Stock
from user_management.models import CustomUser


class Order(models.Model):
    ORDER_STATUS = (
        ("open", "Open"),
        ("closed", "Closed"),
        ("canceled", "Canceled"),
    )

    ORDER_TYPE = (
        ("short", "Short"),
        ("long", "Long"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_type = models.CharField(max_length=5, choices=ORDER_TYPE, blank=True)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    status = models.CharField(max_length=8, choices=ORDER_STATUS, default="open")
    manual = models.BooleanField(default=True)

    def __str__(self):
        return f"Order for {self.quantity} {self.stock.name} by {self.user} - {self.order_type}"
