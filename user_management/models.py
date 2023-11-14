import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from stocks.models import Stock

from .managers import CustomUserManager


def upload_to(instance, filename: str) -> str:
    unique_filename = f"{uuid.uuid4()}.{filename.split('.')[-1].lower()}"
    return f"{settings.AWS_S3_USER_AVATARS_LOCATION}/{unique_filename}"


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("analyst", "Analyst"),
        ("admin", "Admin"),
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    subscriptions = models.ManyToManyField(Stock)

    avatar = models.ImageField(storage=S3Boto3Storage(), upload_to=upload_to, null=True, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"
