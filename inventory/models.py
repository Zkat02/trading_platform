from django.db import models

from stocks.models import Stock
from user_management.models import CustomUser


class Inventory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} has {self.quantity} shares of {self.stock.name}"
