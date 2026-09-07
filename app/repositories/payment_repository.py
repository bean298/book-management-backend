import uuid

from sqlalchemy import select

from app.models.payment_model import Payment
from app.orm.repository import Repository


class PaymentRepository(Repository[Payment]):
    def __init__(self, session):
        super().__init__(session, Payment)

    # Def to get list payment of order
    async def get_list_by_order_id(self, order_id: str) -> list[Payment]:
        stmt = select(Payment).where(Payment.order_id == uuid.UUID(str(order_id)))
        result = await self.session.execute(stmt)
        return result.scalars().all()
