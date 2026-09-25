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

    # Def to get payment by transaction_ref
    async def get_payment_by_transaction_ref(self, transaction_ref: str) -> Payment:
        stmt = select(Payment).where(Payment.transaction_ref == transaction_ref)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Def to get payment by user_id
    async def get_payment_by_user_id(self, user_id: str) -> list[Payment]:
        stmt = select(Payment).where(Payment.user_id == uuid.UUID(str(user_id)))
        result = await self.session.execute(stmt)
        return result.scalars().all()
