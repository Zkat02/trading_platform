import unittest  # noqa: E402

import django

django.setup()

from orders.models import Order  # noqa: E402
from orders.services import OrderService  # noqa: E402
from stocks.models import Stock  # noqa: E402
from stocks.services import StockService  # noqa: E402
from user_management.models import CustomUser  # noqa: E402


class TestCheckConditionForClose(unittest.TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="tuser1", email="user1@example.com", password="password1"
        )
        self.stock = Stock.objects.create(
            name="tStock 1", symbol="FS1", price_per_unit_sail=120, price_per_unit_buy=110
        )

        self.order_long_sell = Order.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=1,
            status="open",
            manual=False,
            user_action_type="sell",
            price_limit=100,
            order_type="long",
        )

        self.order_short_sell = Order.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=1,
            status="open",
            manual=False,
            user_action_type="sell",
            price_limit=100,
            order_type="short",
        )

        self.order_long_buy = Order.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=1,
            status="open",
            manual=False,
            user_action_type="buy",
            price_limit=100,
            order_type="long",
        )

        self.order_short_buy = Order.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=1,
            status="open",
            manual=False,
            user_action_type="buy",
            price_limit=100,
            order_type="short",
        )

        self.order_service = OrderService()

    def test_long_sell_condition(self):
        # Проверка условия для долгой продажи, ждем пока цена упадет
        self.stock.price_per_unit_buy = 120
        self.assertFalse(self.order_service.is_ready_to_close(self.order_long_sell))
        self.stock.price_per_unit_buy = 80
        self.assertTrue(self.order_service.is_ready_to_close(self.order_long_sell))

    def test_long_buy_condition(self):
        # Проверка условия для долгой покупки, ждем пока цена упадет
        self.stock.price_per_unit_sail = 130
        self.assertFalse(self.order_service.is_ready_to_close(self.order_long_buy))
        self.stock.price_per_unit_sail = 80
        self.assertTrue(self.order_service.is_ready_to_close(self.order_long_buy))

    def test_short_buy_condition(self):
        # Проверка условия для быстрой покупки, ждем пока цена акции вырастет до лимита
        self.stock.price_per_unit_sail = 80
        self.assertFalse(self.order_service.is_ready_to_close(self.order_short_buy))
        self.stock.price_per_unit_sail = 130
        self.assertTrue(self.order_service.is_ready_to_close(self.order_short_buy))

    def test_short_sell_condition(self):
        # Проверка условия для быстрой продажи, ждем пока цена акции вырастет до лимита
        self.stock.price_per_unit_buy = 80
        self.assertFalse(self.order_service.is_ready_to_close(self.order_short_sell))
        self.stock.price_per_unit_buy = 130
        self.assertTrue(self.order_service.is_ready_to_close(self.order_short_sell))

    def tearDown(self):
        self.user.delete()
        self.stock.delete()
        self.order_long_sell.delete()
        self.order_short_sell.delete()
        self.order_long_buy.delete()
        self.order_short_buy.delete()


if __name__ == "__main__":
    unittest.main()
