from app.orm.repository import Repository
from app.models.cart_model import Cart
from sqlalchemy import select
import uuid


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
