from fastapi import UploadFile

from app.configs import config
from app.core.s3_minio import minio_service
from app.db.database import IUnitOfWork
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.models.book_model import Book
from app.schemas.base_schema import AppBasePagingRes
from app.schemas.book_schema import (
    BookRes,
    CreateBookReq,
    UpdateBookReq,
    book_to_res,
    req_to_book,
)


# Create new book (with optional cover image via multipart)
async def create_book(
    book_data: CreateBookReq,
    uow: IUnitOfWork,
    image: UploadFile | None = None,
) -> BookRes:
    # Check existing book title
    existing_book = await uow.books.get_book_by_title(book_data.title)
    if existing_book:
        raise ValueError(f"Book with title {book_data.title} already exists.")

    book = req_to_book(book_data)
    new_book = await uow.books.add(book)

    # Upload cover image if provided
    if image and image.filename and image.size and image.size > 0:
        object_name, err = await minio_service.upload_image(
            bucket=config.MINIO_BUCKET,
            filename=f"books/{new_book.id}/{image.filename}",
            image=image,
        )
        if err:
            logger.error(
                "Failed to upload cover | book_id=%s, error=%s", new_book.id, err
            )
            raise ValueError(f"Failed to upload image: {err}")
        new_book.cover_image = object_name

    logger.info(
        "Book created | id=%s, title=%s, slug=%s",
        new_book.id,
        new_book.title,
        new_book.slug,
    )
    return book_to_res(new_book)


# Update book
async def update_book(
    book_id: str,
    book_data: UpdateBookReq,
    uow: IUnitOfWork,
    image: UploadFile | None = None,
) -> BookRes:
    """
    Args:
        book_id (str): [description]
        book_data (UpdateBookReq): [description]
        uow (IUnitOfWork): [description]
        image (Optional[UploadFile], optional): [description]. Defaults to None.

    Raises:
        NotFoundError: [description]
        ValueError: [description]

    Returns:
        BookRes: [description]
    """

    book = await uow.books.get_by_id(book_id)
    if not book:
        raise NotFoundError()

    # Keep the old cover by default (in case no new image is provided)
    new_image = book.cover_image

    # Upload new image (if any)
    if image and image.filename and image.size and image.size > 0:
        new_image, err = await minio_service.upload_image(
            bucket=config.MINIO_BUCKET,
            filename=f"books/{book.id}/{image.filename}",
            image=image,
        )
        if err:
            logger.error("Failed to upload cover | book_id=%s, error=%s", book.id, err)
            raise ValueError(f"Failed to upload image: {err}")

        # Delete the old image only AFTER the new one is uploaded successfully,
        # and only if it's a different object (same filename = overwrite).
        if book.cover_image and book.cover_image != new_image:
            try:
                minio_service.delete_file(
                    bucket=config.MINIO_BUCKET,
                    object_name=book.cover_image,
                )
            except Exception as e:
                logger.warning(f"Failed to delete old image {book.cover_image}: {e}")

    book.cover_image = new_image

    update_data = book_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    logger.info(f"Book updated: id={book_id}")

    return book_to_res(book)


# Delete book
async def delete_book(book_id: str, uow: IUnitOfWork) -> None:
    """
    Args:
        book_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]
    """

    book = await uow.books.get_by_id(book_id)
    if not book:
        raise ValueError(f"Book with id {book_id} not found.")

    # Delete images from MinIO before deleting DB record
    if book.cover_image:
        try:
            minio_service.delete_file(config.MINIO_BUCKET, book.cover_image)
        except Exception as e:
            logger.warning(f"Failed to delete image {book.cover_image}: {e}")

    await uow.books.delete(book)

    logger.info(f"Book deleted: id={book_id}")


# Get list books
async def list_books(
    uow: IUnitOfWork,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> AppBasePagingRes[BookRes]:
    if keyword:
        condition = Book.title.icontains(f"%{keyword}%")
        paging = await uow.books.paginate(
            condition,
            page=page,
            page_size=page_size,
        )
    else:
        paging = await uow.books.paginate(
            page=page,
            page_size=page_size,
        )

    return AppBasePagingRes[BookRes](
        items=[book_to_res(b) for b in paging.items],
        total=paging.total,
        page=paging.page,
        page_size=paging.page_size,
        is_full=paging.is_full,
    )


# Get book by id
async def get_book(
    book_id: str,
    uow: IUnitOfWork,
) -> BookRes:
    book = await uow.books.get_by_id(book_id)
    if not book:
        raise NotFoundError()

    return book_to_res(book)
