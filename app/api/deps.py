from fastapi import Depends
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

# take token from request header (Bearer <token>)
http_bearer = HTTPBearer()


# Dependencies: get and check token of user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Dependency: Take user's information from JWT Token
    - Decode token from header Authorization -> payload
    - Take user_id from payload
    - If token expired | invalid -> raise ExpiredTokenError | InvalidTokenError
    - If user don't exist -> raise UserNotFoundError
    - If user exist -> return user (Use for API, those need authorization)
    """
    try:
        # Verify token
        payload = jwt.decode(
            credentials.credentials,
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
