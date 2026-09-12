from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode
from uuid import uuid4

from app.configs import config
from app.constants.vnpay import VNP_ERROR_MESSAGES
from app.db.database import IUnitOfWork
from app.enum.common import OrderStatus, PaymentMethod, PaymentStatus
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.models.payment_model import Payment
from app.schemas.payment_schema import CreatePaymentReq, PaymentUrlRes, payment_to_res
from app.utils.vnpay import build_payment_url, parse_vnpay_date, verify_payment


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


# Verify payment from VNPay and redirect to screen success/fail
async def process_return(params: dict, uow: IUnitOfWork) -> str:
    status = "invalid"
    message = "Signature in invalid"
    payment = None

    try:
        # Verify payment
        vnp = verify_payment(params)

        # Get res code and set status/message
        response_code = vnp.get("vnp_ResponseCode", "")
        status = "success" if response_code == "00" else "failed"
        message = (
            "Payment successful"
            if status == "success"
            else VNP_ERROR_MESSAGES.get(response_code, "Payment failed")
        )

        # Update order, payment in database
        await _apply_callback_into_db(vnp, uow)

        # Get payment by transaction_ref
        payment = await uow.payment.get_payment_by_transaction_ref(
            vnp.get("vnp_TxnRef", "")
        )
    except ValueError:
        pass
    except Exception:
        logger.exception("Return callback error")
        message = "System error, please try again"

    # payment_result: contain the payment result to return to frontend
    payment_result = {
        "status": status,
        "message": message,
        "txn_ref": params.get("vnp_TxnRef", ""),
    }

    # add more information of payment into payment_result{}
    if payment:
        payment_result.update(
            {
                "order_id": str(payment.order_id),
                "amount": f"{payment.amount:,.0f}",
                "gateway_txn_no": payment.gateway_txn_no or "",
                "method": payment.payment_method.label,
                "pay_date": (
                    payment.pay_date.strftime("%H:%M %d/%m/%Y")
                    if payment.pay_date
                    else ""
                ),
            }
        )

    return f"/payment-result?{urlencode(payment_result)}"


# HELPER: Update payment, order model after VNPay callback
async def _apply_callback_into_db(vnpay: dict, uow: IUnitOfWork) -> tuple[str, str]:

    # Get payment by transaction ref
    payment = await uow.payment.get_payment_by_transaction_ref(vnpay["vnp_TxnRef"])
    if not payment:
        return "01", "Order not found"

    # Check money amount
    vnp_amount = int(vnpay.get("vnp_Amount", "0"))
    expected_amount = int(round(payment.amount * 100))
    if vnp_amount != expected_amount:
        return "04", "Invalid amount"

    # Check if payment is still pending
    if payment.status != PaymentStatus.PENDING:
        return "02", "Order already confirmed"

    payment.raw_callback = vnpay

    # Check payment status from VNPay response code
    if vnpay.get("vnp_ResponseCode") == "00":
        payment.status = PaymentStatus.SUCCESS
        payment.gateway_txn_no = vnpay.get("vnp_TransactionNo")
        payment.bank_code = vnpay.get("vnp_BankCode")
        payment.pay_date = parse_vnpay_date(vnpay.get("vnp_PayDate"))
        payment.expires_at = None

        # Update order status to CONFIRMED
        order = await uow.order.get_order_by_id_with_items(str(payment.order_id))
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CONFIRMED
            order.expires_at = None

        logger.info(
            "Payment success | payment_id=%s, order_id=%s, txn_ref=%s",
            payment.id,
            payment.order_id,
            vnpay.get("vnp_TxnRef"),
        )

    else:
        payment.status = PaymentStatus.FAILED
        payment.error_message = f"VNPay response code: {vnpay.get('vnp_ResponseCode')}"
        payment.expires_at = None

        # Case user cancel payment, then cancel order and restock book
        response_code = vnpay.get("vnp_ResponseCode", "")
        if response_code == "24":
            order = await uow.order.get_order_by_id_with_items(str(payment.order_id))
            if order and order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CANCELLED
                order.expires_at = None

                # Restock book quantity
                for item in order.order_items:
                    book = await uow.books.get_by_id_for_update(str(item.book_id))
                    if book:
                        book.quantity += item.quantity
                        logger.info(
                            "Restock book | book_id=%s, quantity=%s, order_id=%s",
                            book.id,
                            item.quantity,
                            order.id,
                        )

                logger.info(
                    "Order cancelled due to customer cancel | order_id=%s, code=%s",
                    order.id,
                    response_code,
                )

    return "00", "Confirm payment result from successful"
