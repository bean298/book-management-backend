import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.cart_item_model import CartItem
from app.orm.repository import Repository


class CartItemRepository(Repository[CartItem]):
    def __init__(self, session):
        super().__init__(session, CartItem)

    # Get by cartId and bookId
    async def get_by_cart_and_book(
        self, cart_id: uuid.UUID, book_id: uuid.UUID
    ) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == uuid.UUID(cart_id),
            CartItem.book_id == uuid.UUID(book_id),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Get list item of cart
    async def get_list_by_cart_id(
        self,
        cart_id: uuid.UUID,
    ) -> list[CartItem]:
        stmt = (
            select(CartItem)
            .options(selectinload(CartItem.book))
            .where(CartItem.cart_id == uuid.UUID(cart_id))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
