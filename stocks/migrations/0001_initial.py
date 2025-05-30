# Generated by Django 4.2.6 on 2023-10-17 10:12

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("symbol", models.CharField(max_length=10, unique=True)),
                ("price_per_unit_sail", models.DecimalField(decimal_places=2, max_digits=10)),
                ("price_per_unit_buy", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
