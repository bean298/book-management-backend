from app.orm.repository import Repository
from app.models.cart_model import Cart


class CartRepository(Repository[Cart]):
    def __init__(self, session):
        super().__init__(session, Cart)
