import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trading_platform.settings")
app = Celery("trading_platform")
app.conf.broker_connection_retry_on_startup = True
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "check_open_orders_every_minute": {
        "task": "orders.tasks.check_open_orders",
        "schedule": 60.0,
    },
}
