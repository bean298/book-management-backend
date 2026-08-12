from app.db.database import IUnitOfWork
from app.logging.logger import logger
from app.schemas.base_schema import AppBasePagingRes
from typing import Optional
from app.schemas.category_schema import (
    CategoryRes,
    UpdateCategoryReq,
    category_to_res,
    CategoryCreateReq,
    req_to_category,
)
from app.exceptions.resource_exception import NotFoundError
from app.models.category_model import Category


# Create new category
async def create_category(
    category_data: CategoryCreateReq, uow: IUnitOfWork
) -> CategoryRes:
    """
    Args:
        category_data (CategoryCreateReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]

    Returns:
        CategoryRes: [description]
    """
    new_category = req_to_category(category_data)
    new_category = await uow.categories.add(new_category)

    logger.info("Category created | id=%s, name=%s", new_category.id, new_category.name)
    return category_to_res(new_category)


# Update category
async def update_category(
    category_id: str, category_data: UpdateCategoryReq, uow: IUnitOfWork
) -> CategoryRes:
    """
    Args:
        category_id (str): [description]
        category_data (UpdateCategoryReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        CategoryRes: [description]
    """

    category = await uow.categories.get_by_id(category_id)
    if not category:
        raise NotFoundError()

    update_data = category_data.model_dump(
        exclude_unset=True, exclude_none=True
    )  # skip None, skip field haven't set

    for field, value in update_data.items():
        setattr(category, field, value)

    logger.info("Category updated: id=%s", category_id)
    return category_to_res(category)


# Delete category
async def delete_category(category_id: str, uow: IUnitOfWork):
    """
    Args:
        category_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]
    """

    category = await uow.categories.get_by_id(category_id)
    if not category:
        raise NotFoundError()

    await uow.categories.delete(category)
    logger.info("Category deleted: id=%s", category_id)


# Get list categories
async def list_categories(
    uow: IUnitOfWork,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> AppBasePagingRes[CategoryRes]:
    if keyword:
        condition = Category.name.icontains(f"%{keyword}%")

        paging = await uow.categories.paginate(
            condition,
            page=page,
            page_size=page_size,
        )
    else:
        paging = await uow.categories.paginate(
            page=page,
            page_size=page_size,
        )
    return AppBasePagingRes[CategoryRes](
        items=[category_to_res(p) for p in paging.items],
        total=paging.total,
        page=paging.page,
        page_size=paging.page_size,
        is_full=paging.is_full,
    )


# Get category
async def get_category(
    category_id: str,
    uow: IUnitOfWork,
) -> CategoryRes:
    """
    Args:
        category_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        CategoryRes: [description]
    """
    category = await uow.categories.get_by_id(category_id)
    if not category:
        raise NotFoundError()

    return category_to_res(category)
