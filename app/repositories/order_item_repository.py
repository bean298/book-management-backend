from app.models.order_item_model import OrderItem
from app.orm.repository import Repository


class OrderItemRepository(Repository[OrderItem]):
    def __init__(self, session):
        super().__init__(session, OrderItem)
