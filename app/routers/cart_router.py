from fastapi import APIRouter, Depends
from app.db.database import IUnitOfWork, get_uow
from app.services import cart_service
from app.api.deps import get_current_user
from app.schemas.cart_schema import CartRes
from app.schemas.cart_item_schema import AddToCartReq
from app.schemas.base_schema import AppBaseResponse
from app.utils.common import Error400
from app.models.user_model import User

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post(
    "/items",
    response_model=AppBaseResponse[CartRes],
    summary="Add a book to cart",
)
async def add_to_cart(
    data: AddToCartReq,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    async with uow:
        try:
            cart = await cart_service.add_to_cart(
                user_id=current_user.id,
                data=data,
                uow=uow,
            )

            return AppBaseResponse(
                data=cart,
                message="Added to cart successfully",
            )
        except ValueError as ex:
            return Error400(str(ex))
