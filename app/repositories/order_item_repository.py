from app.orm.repository import Repository
from app.models.order_item_model import OrderItem


class OrderItemRepository(Repository[OrderItem]):
    def __init__(self, session):
        super().__init__(session, OrderItem)
