from app.db.database import IUnitOfWork
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger
from app.models.author_model import Author
from app.schemas.author_schema import (
    AuthorCreateReq,
    AuthorRes,
    UpdateAuthorReq,
    author_to_res,
    req_to_author,
)
from app.schemas.base_schema import AppBasePagingRes


# Create new author
async def create_author(author_data: AuthorCreateReq, uow: IUnitOfWork) -> AuthorRes:
    """
    Args:
        author_data (AuthorCreateReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]

    Returns:
        AuthorRes: [description]
    """

    # Check existing name
    existing_author = await uow.authors.get_author_by_name(author_data.name)
    if existing_author:
        raise ValueError(f"Author with name {author_data.name} already exists.")

    # Create new author
    author = req_to_author(author_data)
    new_author = await uow.authors.add(author)

    logger.info("Author registered | id=%s, name=%s", new_author.id, new_author.name)
    return author_to_res(new_author)


# Update author
async def update_author(
    author_id: str, author_data: UpdateAuthorReq, uow: IUnitOfWork
) -> AuthorRes:
    """
    Args:
        author_id (str): [description]
        author_data (UpdateAuthorReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        AuthorRes: [description]
    """

    author = await uow.authors.get_by_id(author_id)
    if not author:
        raise NotFoundError()

    update_author = author_data.model_dump(
        exclude_unset=True, exclude_none=True
    )  # skip None, skip field haven't set

    for field, value in update_author.items():
        setattr(author, field, value)

    logger.info(f"Author updated: id={author_id}")

    return author_to_res(author)


# Delete author
async def delete_author(author_id: str, uow: IUnitOfWork) -> AuthorRes:
    """
    Args:
        author_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        AuthorRes: [description]
    """

    author = await uow.authors.get_by_id(author_id)
    if not author:
        raise NotFoundError()

    await uow.authors.delete(author)

    logger.info(f"Author deleted: id={author_id}")


# Get list authors
async def list_authors(
    uow: IUnitOfWork,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> AppBasePagingRes[AuthorRes]:
    if keyword:
        condition = Author.name.icontains(f"%{keyword}%")

        paging = await uow.authors.paginate(
            condition,
            page=page,
            page_size=page_size,
        )
    else:
        paging = await uow.authors.paginate(
            page=page,
            page_size=page_size,
        )
    return AppBasePagingRes[AuthorRes](
        items=[author_to_res(p) for p in paging.items],
        total=paging.total,
        page=paging.page,
        page_size=paging.page_size,
        is_full=paging.is_full,
    )


# Get author
async def get_author(
    author_id: str,
    uow: IUnitOfWork,
) -> AuthorRes:
    """
    Args:
        author_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        AuthorRes: [description]
    """
    author = await uow.authors.get_by_id(author_id)
    if not author:
        raise NotFoundError()

    return author_to_res(author)
