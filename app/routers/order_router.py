from fastapi import APIRouter, Depends, Query
from app.db.database import IUnitOfWork, get_uow
from app.utils.common import Error400
from app.api.deps import require_admin, get_current_user
from app.schemas.order_schema import CreateOrderReq, OrderRes
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.models.user_model import User
from app.services import order_service
from typing import Optional
from app.enum.common import OrderStatus

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


# Get list orders of user
@router.get(
    "/my-orders",
    summary="Get my orders (paging)",
    response_model=AppBaseResponse[AppBasePagingRes[OrderRes]],
)
async def get_my_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    status: Optional[OrderStatus] = Query(
        default=None, description="Filter order status"
    ),
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    try:
        async with uow:
            orders = await order_service.list_orders(
                str(current_user.id),
                uow,
                page=page,
                page_size=page_size,
                status=status,
            )
            return AppBaseResponse[AppBasePagingRes[OrderRes]](data=orders)
    except ValueError as ex:
        return Error400(str(ex))


# Get list orders for admin
@router.get(
    "/all-orders",
    summary="Get all orders (admin, paging)",
    response_model=AppBaseResponse[AppBasePagingRes[OrderRes]],
)
async def get_all_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    status: Optional[OrderStatus] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    try:
        async with uow:
            orders = await order_service.list_orders_admin(
                uow, page=page, page_size=page_size, status=status, user_id=user_id
            )
            return AppBaseResponse[AppBasePagingRes[OrderRes]](data=orders)
    except ValueError as ex:
        return Error400(str(ex))


# Get order
@router.get(
    "/{order_id}",
    summary="Get order",
)
async def get_order(
    order_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    try:
        async with uow:
            res = await order_service.get_order(order_id, str(current_user.id), uow)
            return AppBaseResponse(data=res)
    except ValueError as ex:
        return Error400(str(ex))
