from fastapi import Depends, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)  # Take token from header
from jose import JWTError, jwt  # Create JWT

from app.configs import config
from app.db.database import IUnitOfWork, get_uow
from app.exceptions.auth_exception import (
    AdminAccessRequiredError,
    UserNotFoundError,
)
from app.exceptions.token_exception import ExpiredTokenError, InvalidTokenError
from app.models.user_model import User

# Optional header: take token from request header (Bearer <token>)
http_bearer = HTTPBearer(auto_error=False)


# Dependencies: get and check token of user
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Dependency: Authenticate user using an access token.
    - Extract access token from Cookie first, then Authorization header.
    - If no token is provided -> raise InvalidTokenError.
    - Decode and validate JWT token.
    - If token is expired or invalid -> raise appropriate token error.
    - Extract user_id from token payload.
    - Retrieve user from database.
    - If user does not exist -> raise UserNotFoundError.
    - If user exists -> return User object.
    """
    token = request.cookies.get(config.ACCESS_COOKIE_NAME) or (
        credentials.credentials if credentials else None
    )
    if not token:
        raise InvalidTokenError("Missing access token")

    try:
        # Verify token
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            raise InvalidTokenError("Not an access token")

        # Get user id in payload
        user_id: str = payload.get("id")
        if user_id is None:
            raise InvalidTokenError("Invalid token payload")

    except JWTError as err:
        raise ExpiredTokenError() from err

    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
    return user


# Dependencies: get, check token of user and role of user
async def require_admin(
    current_user: User = Depends(get_current_user),
):
    """
    Dependency: Require Admin role
    - Take current_user from dependency get_current_user
    - Check role of user is "admin" ?
    - No -> raise AdminAccessRequiredError
    - Yes -> return current_user
    """
    if current_user.role.value != "admin":
        raise AdminAccessRequiredError()
    return current_user
