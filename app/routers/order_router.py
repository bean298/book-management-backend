from fastapi import APIRouter, Depends, Query
from app.db.database import IUnitOfWork, get_uow
from app.utils.common import Error400
from app.api.deps import require_admin, get_current_user
from app.schemas.order_schema import CreateOrderReq, OrderRes
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.models.user_model import User
from app.services import order_service

router = APIRouter(prefix="/order", tags=["Order"])


# Chekout cart
@router.post(
    "/checkout",
    response_model=AppBaseResponse[OrderRes],
    summary="Create order",
)
async def checkout(
    cart_id: str,
    data: CreateOrderReq,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    try:
        async with uow:

            order = await order_service.checkout(current_user.id, cart_id, data, uow)
            return AppBaseResponse(
                data=order,
                message="Create order successfully",
            )
    except ValueError as ex:
        return Error400(str(ex))
