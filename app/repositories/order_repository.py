from app.orm.repository import Repository
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from sqlalchemy import select
import uuid
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from app.enum.common import OrderStatus


class OrderRepository(Repository[Order]):
    def __init__(self, session):
        super().__init__(session, Order)

    # Get orders of a user with pagination
    async def get_list_paginate_orders_by_user_id(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        status: OrderStatus | None = None,
    ) -> dict:
        conditions = [Order.user_id == uuid.UUID(str(user_id))]
        if status:
            conditions.append(Order.status == status)

        stmt = (
            select(Order)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.book),
                selectinload(Order.user),
            )
            .where(*conditions)
            .order_by(Order.created_at.desc())
        )

        # Total order SELECT COUNT(*)
        count_stmt = (
            select(func.count()).select_from(Order).where(*conditions)
        )  # Create SQL statement
        total = await self.session.scalar(count_stmt)  # Execute SQL statement

        # Pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        items = result.scalars().unique().all()

        # Return dictionary
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "is_full": page_size * page >= total,
        }

    # Get order by id with order items, book and user
    async def get_order_by_id_with_items(self, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.book),
                selectinload(Order.user),
            )
            .where(Order.id == uuid.UUID(str(order_id)))
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Get all order
    async def get_all_orders(
        self,
        page: int = 1,
        page_size: int = 10,
        status: OrderStatus | None = None,
    ) -> dict:
        pass
