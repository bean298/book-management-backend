from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse

from app.api.deps import get_current_user
from app.db.database import IUnitOfWork, get_uow
from app.models.user_model import User
from app.schemas.base_schema import AppBaseResponse
from app.schemas.payment_schema import CreatePaymentReq, PaymentUrlRes
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
