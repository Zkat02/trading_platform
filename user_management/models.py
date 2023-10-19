from django.contrib.auth.models import AbstractUser
from django.db import models

from stocks.models import Stock

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("analyst", "Analyst"),
        ("admin", "Admin"),
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    subscriptions = models.ManyToManyField(Stock)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"

