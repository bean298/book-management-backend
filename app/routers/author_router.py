from fastapi import APIRouter, Depends, Query

from app.api.deps import require_admin
from app.db.database import IUnitOfWork, get_uow
from app.schemas.author_schema import (
    AuthorCreateReq,
    AuthorRes,
    UpdateAuthorReq,
)
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.services import author_service
from app.utils.common import Error400

router = APIRouter(prefix="/author", tags=["Author"])


# Create new author
@router.post("", summary="Create a new author", response_model=AuthorRes)
async def create_author(
    data: AuthorCreateReq,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            res = await author_service.create_author(data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Get list authors
@router.get(
    "",
    summary="List authors",
    response_model=AppBaseResponse[AppBasePagingRes[AuthorRes]],
)
async def get_authors(
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        authors = await author_service.list_authors(
            uow,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return AppBaseResponse[AppBasePagingRes[AuthorRes]](data=authors)


# Get author
@router.get(
    "/{author_id}",
    summary="Get author",
)
async def get_author_detail(
    author_id: str,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            res = await author_service.get_author(author_id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Update author
@router.put(
    "/{author_id}",
    summary="Update a author",
    response_model=AuthorRes,
)
async def update_author(
    author_id: str,
    data: UpdateAuthorReq,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            res = await author_service.update_author(author_id, data, uow)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Delete author
@router.delete(
    "/{author_id}",
    summary="Delete a author",
    response_model=AppBaseResponse,
)
async def delete_author(
    author_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            await author_service.delete_author(author_id, uow)
            return AppBaseResponse(message="Author deleted successfully")
        except ValueError as ex:
            return Error400(str(ex))
