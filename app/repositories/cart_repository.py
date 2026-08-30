import uuid

from sqlalchemy import select

from app.models.cart_model import Cart
from app.orm.repository import Repository


class CartRepository(Repository[Cart]):
    def __init__(self, session):
        super().__init__(session, Cart)

    # Get cart by user id
    async def get_cart_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> Cart:
        stmt = select(Cart).where(Cart.user_id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        return result.scalars().first()
