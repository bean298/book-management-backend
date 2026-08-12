from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.database import IUnitOfWork, get_uow
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.services import category_service
from app.utils.common import Error400
from app.api.deps import require_admin
from app.schemas.category_schema import (
    CategoryCreateReq,
    UpdateCategoryReq,
    CategoryRes,
)

router = APIRouter(prefix="/category", tags=["Category"])


# Create new category
@router.post("", summary="Create a new category", response_model=CategoryRes)
async def create_category(
    data: CategoryCreateReq,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            res = await category_service.create_category(data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Get list categories
@router.get(
    "",
    summary="List categories",
    response_model=AppBaseResponse[AppBasePagingRes[CategoryRes]],
)
async def get_categories(
    keyword: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        categories = await category_service.list_categories(
            uow,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return AppBaseResponse[AppBasePagingRes[CategoryRes]](data=categories)


# Get category
@router.get(
    "/{category_id}",
    summary="Get category",
)
async def get_category_detail(
    category_id: str,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            res = await category_service.get_category(category_id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Update category
@router.put(
    "/{category_id}",
    summary="Update a category",
    response_model=CategoryRes,
)
async def update_category(
    category_id: str,
    data: UpdateCategoryReq,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            res = await category_service.update_category(category_id, data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Delete category
@router.delete(
    "/{category_id}",
    summary="Delete a category",
    response_model=AppBaseResponse,
)
async def delete_category(
    category_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            await category_service.delete_category(category_id, uow)
            return AppBaseResponse(message="Category deleted successfully")
        except ValueError as ex:
            return Error400(str(ex))
