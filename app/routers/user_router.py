from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.database import IUnitOfWork, get_uow
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.services import user_service
from app.schemas.user_schema import UserRes, UpdateUserReq, UserCreateReq
from app.utils.common import Error400

router = APIRouter(prefix="/user", tags=["User"])


# Create new user
@router.post(
    "",
    summary="Create a new user",
    response_model=UserRes,
)
async def create_user(data: UserCreateReq, uow: IUnitOfWork = Depends(get_uow)):
    async with uow:
        try:
            res = await user_service.create_user(data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Get list users
@router.get(
    "",
    summary="List users",
    response_model=AppBaseResponse[AppBasePagingRes[UserRes]],
)
async def get_users(
    keyword: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        users = await user_service.list_users(
            uow,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return AppBaseResponse[AppBasePagingRes[UserRes]](data=users)


# Get user
@router.get("/{user_id}", summary="Get user")
async def get_user_detail(
    user_id: str,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            res = await user_service.get_user(user_id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Update user
@router.put(
    "/{user_id}",
    summary="Update a user",
    response_model=UserRes,
)
async def update_user(
    user_id: str,
    data: UpdateUserReq,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            res = await user_service.update_user(user_id, data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Delete user
@router.delete(
    "/{user_id}",
    summary="Delete a user",
    response_model=AppBaseResponse,
)
async def delete_user(
    user_id: str,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            await user_service.delete_user(user_id, uow)
            return AppBaseResponse(message="User deleted successfully")
        except ValueError as ex:
            return Error400(str(ex))
