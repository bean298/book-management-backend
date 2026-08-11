from typing import Optional
from app.db.database import IUnitOfWork
from app.models.user_model import User
from app.logging.logger import logger
from app.schemas.base_schema import AppBasePagingRes
from app.schemas.user_schema import (
    UserCreateReq,
    UserRes,
    req_to_user,
    user_to_res,
    UpdateUserReq,
)
from app.exceptions.resource_exception import NotFoundError
from app.logging.logger import logger


# Create new user
async def create_user(user_data: UserCreateReq, uow: IUnitOfWork) -> UserRes:
    """
    Args:
        user_data (UserCreateReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        ValueError: [description]

    Returns:
        UserRes: [description]
    """

    # Check existing email
    existing_user = await uow.users.get_user_by_email(user_data.email)
    if existing_user:
        raise ValueError(f"User with email {user_data.email} already exists.")

    # Create new user
    user = req_to_user(user_data)
    new_user = await uow.users.add(user)
    await uow.commit()

    logger.info("User registered | id=%s, email=%s", new_user.id, new_user.email)
    return user_to_res(new_user)


# Update user
async def update_user(
    user_id: str, user_data: UpdateUserReq, uow: IUnitOfWork
) -> UserRes:
    """
    Args:
        user_id (str): [description]
        user_data (UpdateUserReq): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        UserRes: [description]
    """

    user = await uow.users.get_by_id(user_id)
    if not user:
        raise NotFoundError()

    update_user = user_data.model_dump(
        exclude_unset=True, exclude_none=True
    )  # skip None, skip field haven't set

    for field, value in update_user.items():
        setattr(user, field, value)

    await uow.commit()

    logger.info(f"User updated: id={user_id}")

    return user_to_res(user)


# Delete user
async def delete_user(user_id: str, uow: IUnitOfWork) -> UserRes:
    """
    Args:
        user_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        UserRes: [description]
    """

    user = await uow.users.get_by_id(user_id)
    if not user:
        raise NotFoundError()

    await uow.users.delete(user)
    await uow.commit()

    logger.info(f"User deleted: id={user_id}")


# Get list users
async def list_users(
    uow: IUnitOfWork,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> AppBasePagingRes[UserRes]:

    if keyword:
        condition = User.name.icontains(f"%{keyword}%")

        paging = await uow.users.paginate(
            condition,
            page=page,
            page_size=page_size,
        )
    else:
        paging = await uow.users.paginate(
            page=page,
            page_size=page_size,
        )

    return AppBasePagingRes[UserRes](
        items=[user_to_res(p) for p in paging.items],
        total=paging.total,
        page=paging.page,
        page_size=paging.page_size,
        is_full=paging.is_full,
    )


# Get user
async def get_user(
    user_id: str,
    uow: IUnitOfWork,
) -> UserRes:
    """
    Args:
        user_id (str): [description]
        uow (IUnitOfWork): [description]

    Raises:
        NotFoundError: [description]

    Returns:
        UserRes: [description]
    """

    user = await uow.users.get_by_id(user_id)
    if not user:
        raise NotFoundError()

    return user_to_res(user)
