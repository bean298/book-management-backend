from datetime import datetime

from pydantic import BaseModel, Field

from app.enum.common import PaymentMethod, PaymentStatus
from app.models.payment_model import Payment


class CreatePaymentReq(BaseModel):
    """Schema for creating a new payment"""

    method: PaymentMethod = Field(..., description="Payment method")


class PaymentRes(BaseModel):
    """Schema for payment response."""

    id: str = Field(..., description="Payment ID")
    order_id: str = Field(..., description="Order ID")
    amount: float = Field(..., description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    status: PaymentStatus = Field(..., description="Payment status")
    transaction_ref: str = Field(
        ..., description="Transaction reference sent to the payment gateway"
    )
    gateway_txn_no: str | None = Field(
        default=None, description="Transaction number returned by the gateway"
    )
    bank_code: str | None = Field(
        default=None, description="Bank code of the customer's bank"
    )
    pay_date: datetime | None = Field(
        default=None, description="Payment date confirmed by the gateway"
    )
    ip_address: str | None = Field(default=None, description="IP address of the customer")
    error_message: str | None = Field(
        default=None, description="Error message if the payment failed"
    )
    created_at: datetime = Field(..., description="Payment created time")


class CreatePaymentUrlRes(BaseModel):
    """Schema returned after creating a payment URL."""

    payment_url: str = Field(..., description="Gateway URL to redirect the customer to")
    payment: PaymentRes = Field(..., description="Payment information")


def payment_to_res(payment: Payment) -> PaymentRes:
    """Convert a Payment ORM model to a PaymentRes schema."""
    return PaymentRes(
        id=str(payment.id),
        order_id=str(payment.order_id),
        user_id=str(payment.user_id),
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_ref=payment.transaction_ref,
        gateway_txn_no=payment.gateway_txn_no,
        bank_code=payment.bank_code,
        pay_date=payment.pay_date,
        ip_address=payment.ip_address,
        error_message=payment.error_message,
        created_at=payment.created_at,
    )
