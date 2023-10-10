from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("analyst", "Analyst"),
        ("admin", "Admin"),
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return self.username
