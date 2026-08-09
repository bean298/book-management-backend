from app.db.database import IUnitOfWork
from app.models.user_model import User
from app.schemas.user_schema import UserCreateReq, user_to_res, req_to_user
from app.schemas.auth_schema import TokenRes, token_to_res
from app.utils.security import hash_password, verify_password, create_access_token
from app.logging.logger import logger
from app.exceptions.auth_exception import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)


# Register new account
async def register(uow: IUnitOfWork, data: UserCreateReq) -> User:
    """
    Args:
        uow (IUnitOfWork): [description]
        data (UserCreateReq): [description]

    Raises:
        EmailAlreadyRegisteredError: [description]

    Returns:
        User: [description]
    """

    # Check existing email
    existing = await uow.users.get_user_by_email(data.email)
    if existing:
        logger.warning("Email already exists | email=%s", data.email)
        raise EmailAlreadyRegisteredError()

    # Create new user
    user = req_to_user(data)
    new_user = await uow.users.add(user)
    await uow.commit()

    logger.info("User registered | id=%s, email=%s", new_user.id, new_user.email)
    return user_to_res(new_user)


# User login, return JWT token
async def login(uow: IUnitOfWork, email: str, password: str) -> TokenRes:
    """
    Args:
        uow (IUnitOfWork): [description]
        email (str): [description]
        password (str): [description]

    Raises:
        InvalidCredentialsError: [description]

    Returns:
        TokenRes: [description]
    """

    # Check existing email and verify password
    user = await uow.users.get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Login failed | email=%s", email)
        raise InvalidCredentialsError()

    # Create new jwt token
    access_token = create_access_token(
        data={"id": str(user.id), "role": user.role.value}
    )
    logger.info("Login successful | user_id=%s", user.id)

    return token_to_res(access_token, user)
