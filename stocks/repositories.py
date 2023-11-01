from base.repositories import BaseRepository
from stocks.models import Stock


class StockRepository(BaseRepository):
    def __init__(self):
        super().__init__(Stock)
        self.model = Stock

    def check_subscription(self, user, stock_id):
        return user.subscriptions.filter(pk=stock_id).exists()

    def get_user_subscriptions(self, user):
        return user.subscriptions
