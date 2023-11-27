import logging

from celery import shared_task

from stocks.services import StockService

logger = logging.getLogger(__name__)


@shared_task
def update_stock_prices():
    StockService().update_stock_prices()
    logger.info("[INFO] celery_task [update_stock_prices]: prices updated successfully.")


@shared_task
def send_stock_symbols_to_kafka():
    StockService().send_stock_symbols_to_kafka()
    logger.info(
        "[INFO] celery_task [send_stock_symbols_to_kafka]:\
              send stock symbols to kafka successfully."
    )
