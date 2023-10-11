from django.db import models

from stoks.models import Stock
from user_management.models import CustomUser


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} subscribed to {self.stock.name}"
