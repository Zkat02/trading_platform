from django.db import models

from stocks.models import Stock
from user_management.models import CustomUser


class Order(models.Model):
    class ORDER_STATUS(models.TextChoices):
        OPEN = "open"
        CLOSED = "closed"
        CANCELED = "canceled"

    class ORDER_TYPE(models.TextChoices):
        SHORT = "short"
        LONG = "long"

    class USER_ACTION_TYPE(models.TextChoices):
        BUY = "buy"
        SELL = "sell"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_type = models.CharField(max_length=5, choices=ORDER_TYPE.choices, blank=True, null=True)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=8, choices=ORDER_STATUS.choices, default=ORDER_STATUS.OPEN)
    user_action_type = models.CharField(max_length=4, choices=USER_ACTION_TYPE.choices)
    manual = models.BooleanField(default=True)
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Order for {self.quantity} {self.stock.name} by {self.user} - {self.order_type}"
