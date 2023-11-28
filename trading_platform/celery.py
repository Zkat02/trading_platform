import os

from celery import Celery
from celery.signals import worker_process_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trading_platform.settings")
app = Celery("trading_platform")
app.conf.broker_connection_retry_on_startup = True
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_process_init.connect
def on_worker_startup(**kwargs):
    """Run the task 1 time when the worker is ready.
    Syncronise stocks in the Django db with MongoDB."""

    from stocks.tasks import send_stock_symbols_to_kafka

    send_stock_symbols_to_kafka.delay()


app.conf.beat_schedule = {
    "check_open_orders_every_minute": {
        "task": "orders.tasks.check_open_orders",
        "schedule": 60.0,
    },
    "update_stock_prices_every_minute": {
        "task": "stocks.tasks.update_stock_prices",
        "schedule": 60.0,
    },
}
