from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse

from app.api.deps import get_current_user, require_admin
from app.db.database import IUnitOfWork, get_uow
from app.enum.common import PaymentMethod, PaymentStatus
from app.models.user_model import User
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.schemas.payment_schema import CreatePaymentReq, PaymentRes, PaymentUrlRes
from app.services import payment_service
from app.utils.common import Error400

router = APIRouter(prefix="/payment", tags=["Payment"])


# Create payment URL for order
@router.post(
    "/",
    response_model=AppBaseResponse[PaymentUrlRes],
    summary="Create a payment for an order",
)
async def create_payment(
    data: CreatePaymentReq,
    order_id: str = Query(..., description="Order ID"),
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    async with uow:
        try:
            # Take IP
            client_ip = request.client.host if request and request.client else "127.0.0.1"

            response = await payment_service.create_payment(
                order_id=order_id,
                user_id=current_user.id,
                data=data,
                uow=uow,
                ip_address=client_ip,
            )

            return AppBaseResponse(data=response, message="Payment created successfully")
        except ValueError as ex:
            return Error400(str(ex))


# VNPay redirect after payment
# After payment, VNPay return command redirect to vnp_ReturnUrl
@router.get("/vnpay/return", include_in_schema=False)
async def vnpay_return(
    request: Request,
    uow: IUnitOfWork = Depends(get_uow),
):
    params = dict(request.query_params)

    async with uow:
        redirect_url = await payment_service.process_return(params, uow)
    return RedirectResponse(url=redirect_url)


# Get list payments (Admin only)
@router.get(
    "",
    summary="List payment (Admin only)",
    response_model=AppBaseResponse[AppBasePagingRes[PaymentRes]],
)
async def list_payments_admin(
    status: PaymentStatus | None = None,
    method: PaymentMethod | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        payments = await payment_service.list_payments_admin(
            uow,
            status=status,
            method=method,
            page=page,
            page_size=page_size,
        )
        return AppBaseResponse[AppBasePagingRes[PaymentRes]](data=payments)


# Get payment of current user
@router.get(
    "/get-payment-of-user",
    summary="Get payment of user (Current user)",
)
async def get_payment_of_user(
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    async with uow:
        try:
            res = await payment_service.get_payment_of_user(current_user.id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))
