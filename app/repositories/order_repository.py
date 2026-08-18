from app.orm.repository import Repository
from app.models.order_model import Order


class OrderRepository(Repository[Order]):
    def __init__(self, session):
        super().__init__(session, Order)
