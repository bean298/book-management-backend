from app.db.database import IUnitOfWork
from app.models.user_model import User
from app.schemas.user_schema import UserCreateReq, user_to_res, req_to_user
from app.schemas.auth_schema import TokenRes, token_to_res
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.logging.logger import logger
from app.exceptions.auth_exception import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from datetime import datetime, timedelta, timezone
from app.models.refresh_token_model import RefreshToken
from app.exceptions.token_exception import (
    InvalidRefreshTokenError,
    RefreshTokenReusedError,
)
from app.configs import config


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

    # Create new jwt token (access token)
    access_token = create_access_token(
        data={"id": str(user.id), "role": user.role.value}
    )

    # Create new refresh token
    raw, token_hash = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=config.REFRESH_TOKEN_EXPIRE_DAYS
    )
    await uow.refresh_tokens.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
    )

    logger.info("Login successful | user_id=%s", user.id)

    # Return access token, refresh token (raw), user information
    return token_to_res(access_token, raw, user)


# Refresh token for user
async def refresh_token(uow: IUnitOfWork, refresh_token_raw: str) -> TokenRes:
    """
    Args:
        uow (IUnitOfWork): [description]
        refresh_token_raw (str): [description]

    Raises:
        InvalidRefreshTokenError: [description]
        RefreshTokenReusedError: [description]
        InvalidRefreshTokenError: [description]
        UserNotFoundError: [description]

    Returns:
        TokenRes: [description]
    """

    # Hash refresh token (received from client)
    token_hash = hash_token(refresh_token_raw)

    # Get refresh token
    stored = await uow.refresh_tokens.get_by_hash(token_hash)
    if not stored:
        raise InvalidRefreshTokenError()

    # Checked token was revoked and replaced or not ?
    if stored.revoked and stored.replaced_by:
        # Revoke all token of user
        # User have to relogin
        await uow.refresh_tokens.revoke_all_by_user(str(stored.user_id))
        await uow.commit()
        raise RefreshTokenReusedError()

    # Checked token was expired or not ?
    if stored.revoked or stored.expires_at < datetime.now(timezone.utc):
        raise InvalidRefreshTokenError()

    user = await uow.users.get_by_id(str(stored.user_id))
    if not user:
        raise UserNotFoundError()

    # Create new refresh token
    raw, new_hash = create_refresh_token()
    new_exp = datetime.now(timezone.utc) + timedelta(
        days=config.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Revoke old token
    await uow.refresh_tokens.revoke(stored, replaced_by=new_hash)

    # Add new refresh token into db
    await uow.refresh_tokens.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=new_exp,
        )
    )

    access_token = create_access_token(
        data={"id": str(user.id), "role": user.role.value}
    )
    return token_to_res(access_token, raw, user)


# Revoke token when user logout
async def logout(uow: IUnitOfWork, refresh_token_raw: str) -> None:
    """
    Args:
        uow (IUnitOfWork): [description]
        refresh_token_raw (str): [description]
    """

    token_hash = hash_token(refresh_token_raw)
    stored = await uow.refresh_tokens.get_by_hash(token_hash)
    if stored:
        await uow.refresh_tokens.revoke(stored)
