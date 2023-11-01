from base.repositories import BaseRepository
from orders.models import Order


class OrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(Order)
        self.model = Order

    def set_status(self, order, status):
        order.status = status
        order.save()

    def close_order(self, order, closing_price):
        order.closing_price = closing_price
        self.set_status(order=order, status="closed")
        order.save()

    def filter_orders(self, **kwargs):
        return self.model.objects.filter(**kwargs)
