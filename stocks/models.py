import uuid

from django.conf import settings
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


def upload_to(instance, filename: str) -> str:
    unique_filename = f"{uuid.uuid4()}.{filename.split('.')[-1].lower()}"
    return f"{settings.AWS_S3_STOCKS_IMAGES_LOCATION}/{unique_filename}"


class Stock(models.Model):
    image = models.ImageField(storage=S3Boto3Storage(), upload_to=upload_to, null=True, blank=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10, unique=True)
    price_per_unit_sail = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit_buy = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name}"
