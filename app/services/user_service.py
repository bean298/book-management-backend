from typing import Optional
from app.db.database import IUnitOfWork
from app.models.user_model import User
from app.logging.logger import logger
from app.schemas.base_schema import AppBasePagingRes
from app.schemas.user_schema import UserCreateReq, UserRes


# Create new user
async def create_user(user_data: UserCreateReq, uow: IUnitOfWork) -> UserRes:
    """Service create new user"""

    existing_user = await uow.users.get_user_by_email(user_data.email)
    if existing_user:
        raise ValueError(f"User with email {user_data.email} already exists.")
