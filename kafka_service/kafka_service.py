import json
import logging
import os
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer

load_dotenv()

logger = logging.getLogger(__name__)


class KafkaService:
    KAFKA_TOPIC_STOCK_PRICES = os.environ.get("KAFKA_TOPIC_STOCK_PRICES")
    KAFKA_TOPIC_STOCK_SYMBOLS = os.environ.get("KAFKA_TOPIC_STOCK_SYMBOLS")
    BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS")

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=self.BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        self.consumer = KafkaConsumer(
            bootstrap_servers=self.BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="earliest",
            group_id="read_stock_prices_group",
            consumer_timeout_ms=1000,
        )

        self.consumer.subscribe([self.KAFKA_TOPIC_STOCK_PRICES])  # topic: "stock_prices"

    def read_stock_prices_from_kafka(self):
        logger.info("start read_stock_prices_from_kafka")
        try:
            for message in self.consumer:
                stocks_data = message.value
                logger.info(f"Data received from Kafka: {stocks_data}")
                yield stocks_data
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            logger.info("end read_stock_prices_from_kafka")

    def send_stock_symbols_to_kafka(self, symbols):
        try:
            logger.info(f"start sending: {symbols}")
            for symbol in symbols:
                self.producer.send(self.KAFKA_TOPIC_STOCK_SYMBOLS, value={"symbol": symbol})
            logger.info(f"Stock symbols {symbols} sent to Kafka successfully")

        except Exception as e:
            logger.error(f"Error sending stock symbols to Kafka: {e}")

    def close_kafka_connection(self):
        self.producer.close()
        self.consumer.close()
