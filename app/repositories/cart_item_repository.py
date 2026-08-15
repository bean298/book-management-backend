from app.orm.repository import Repository
from app.models.cart_item_model import CartItem


class CartItemRepository(Repository[CartItem]):
    def __init__(self, session):
        super().__init__(session, CartItem)
