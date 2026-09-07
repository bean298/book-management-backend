from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.configs import config
from app.db.database import IUnitOfWork
from app.enum.common import OrderStatus, PaymentMethod, PaymentStatus
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.models.payment_model import Payment
from app.schemas.payment_schema import CreatePaymentReq, PaymentUrlRes, payment_to_res
from app.utils.vnpay import build_payment_url


# Create payment
async def create_payment(
    order_id: str,
    user_id: str,
    data: CreatePaymentReq,
    uow: IUnitOfWork,
    ip_address: str = "127.0.0.1",
) -> PaymentUrlRes:
    """Create a new payment for an order."""

    # Get order - order items
    order = await uow.order.get_order_by_id_with_items(order_id)
    if not order:
        raise NotFoundError("Order", order_id)

    # Only the order owner can create a paymen for the order
    if str(order.user_id) != str(user_id):
        raise NotFoundError("Order", order_id)

    # Order must be in PENDING state
    if order.status != OrderStatus.PENDING:
        raise ValueError("Order is not in PENDING state")

    # Check if order has expired
    now = datetime.now(UTC)
    if order.expires_at and order.expires_at < now:
        raise ValueError("Order payment deadline has expired")

    # Check if order already has a pending payment
    payments = await uow.payment.get_list_by_order_id(order_id)
    if any(payment.status == PaymentStatus.PENDING for payment in payments):
        raise ValueError("Order already has a pending payment")

    # Create payment
    payment = await uow.payment.add(
        Payment(
            user_id=order.user_id,
            order_id=order.id,
            amount=order.total_price,
            payment_method=data.method,
            status=PaymentStatus.PENDING,
            expires_at=now + timedelta(minutes=config.PAYMENT_EXPIRY_MINUTES),
            transaction_ref=str(uuid4()),
            ip_address=ip_address,
        )
    )

    # Build payment URL for COD
    if data.method == PaymentMethod.CASH:
        payment_url = None
    else:
        payment_url = build_payment_url(
            amount=payment.amount,
            txn_ref=payment.transaction_ref,
            order_desc=f"Payment for order {order.id}",
            ip_address=ip_address,
            expire_at=order.expires_at,
        )

    logger.info(
        "Payment created | payment_id=%s, order_id=%s, method=%s, amount=%s",
        payment.id,
        order.id,
        data.method.value,
        payment.amount,
    )

    # Return payment URL for COD
    return PaymentUrlRes(payment_url=payment_url, payment=payment_to_res(payment))
