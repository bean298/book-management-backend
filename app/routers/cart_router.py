from fastapi import APIRouter, Depends
from app.db.database import IUnitOfWork, get_uow
from app.services import cart_service
from app.api.deps import get_current_user, require_admin
from app.schemas.cart_schema import CartRes
from app.schemas.cart_item_schema import AddToCartReq
from app.schemas.base_schema import AppBaseResponse
from app.utils.common import Error400
from app.models.user_model import User

router = APIRouter(prefix="/cart", tags=["Cart"])


# Add book to card
@router.post(
    "/add-to-cart",
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


# Get cart of current user
@router.get(
    "/get-cart-of-user",
    summary="Get cart of user (Current user)",
)
async def get_category_detail(
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    async with uow:
        try:
            res = await cart_service.get_cart_of_user(current_user.id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Get cart for admin
@router.get(
    "/{cart_id}",
    summary="Get cart of user (Admin Only)",
)
async def get_category_detail(
    cart_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            res = await cart_service.get_cart(cart_id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Delete cart item in cart
@router.delete(
    "/{cart_item}",
    summary="Delete a cart item",
    response_model=AppBaseResponse,
)
async def delete_cart_item(
    cart_item_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
):
    async with uow:
        try:
            await cart_service.delete_cart_item(cart_item_id, current_user.id, uow)
            return AppBaseResponse(message="Cart item deleted successfully")
        except ValueError as ex:
            return Error400(str(ex))
