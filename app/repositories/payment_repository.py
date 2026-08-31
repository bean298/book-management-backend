from app.models.payment_model import Payment
from app.orm.repository import Repository


class PaymentRepository(Repository[Payment]):
    def __init__(self, session):
        super().__init__(session, Payment)
