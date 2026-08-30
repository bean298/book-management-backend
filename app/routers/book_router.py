from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import require_admin
from app.db.database import IUnitOfWork, get_uow
from app.schemas.base_schema import AppBasePagingRes, AppBaseResponse
from app.schemas.book_schema import BookRes, CreateBookReq, UpdateBookReq
from app.services import book_service
from app.utils.common import Error400

router = APIRouter(prefix="/book", tags=["Book"])


# Create new book (multipart/form-data: form fields + optional image file)
@router.post("", summary="Create a new book", response_model=BookRes)
async def create_book(
    title: str = Form(..., description="Book title"),
    author_id: UUID = Form(..., description="Author ID"),
    category_id: UUID = Form(..., description="Category ID"),
    price: float = Form(..., description="Book price"),
    published_year: int | None = Form(None, description="Published year"),
    quantity: int = Form(0, description="Quantity in stock"),
    description: str | None = Form(None, description="Book description"),
    cover_image: UploadFile | None = File(None, description="Cover image file"),
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            book_data = CreateBookReq(
                title=title,
                author_id=author_id,
                category_id=category_id,
                price=price,
                published_year=published_year,
                quantity=quantity,
                description=description,
            )
            res = await book_service.create_book(book_data, uow, cover_image)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Get list books
@router.get(
    "",
    summary="List books",
    response_model=AppBaseResponse[AppBasePagingRes[BookRes]],
)
async def get_books(
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        books = await book_service.list_books(
            uow,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return AppBaseResponse[AppBasePagingRes[BookRes]](data=books)


# Get book by id
@router.get(
    "/{book_id}",
    summary="Get book",
)
async def get_book(
    book_id: str,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        try:
            res = await book_service.get_book(book_id, uow)
            return AppBaseResponse(data=res)
        except ValueError as ex:
            return Error400(str(ex))


# Update book
@router.put(
    "/{book_id}",
    summary="Update a book (multipart/form-data)",
)
async def update_book(
    book_id: str,
    title: str | None = Form(..., description="Book title"),
    price: float | None = Form(..., description="Book price"),
    published_year: int | None = Form(None, description="Published year"),
    quantity: int | None = Form(0, description="Quantity in stock"),
    description: str | None = Form(None, description="Book description"),
    cover_image: UploadFile | None = File(None, description="Cover image file"),
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            data = UpdateBookReq(
                title=title,
                price=price,
                published_year=published_year,
                quantity=quantity,
                description=description,
            )
            res = await book_service.update_book(book_id, data, uow, cover_image)
            return res
        except ValueError as ex:
            return Error400(str(ex))


# Delete book
@router.delete(
    "/{book_id}",
    summary="Delete a book",
    response_model=AppBaseResponse,
)
async def delete_book(
    book_id: str,
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    async with uow:
        try:
            await book_service.delete_book(book_id, uow)
            return AppBaseResponse(message="Book deleted successfully")
        except ValueError as ex:
            return Error400(str(ex))
