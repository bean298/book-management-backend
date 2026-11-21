from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response

from app.api.deps import get_current_user
from app.configs import config
from app.db.database import IUnitOfWork, get_uow
from app.exceptions.token_exception import InvalidRefreshTokenError
from app.models.user_model import User
from app.schemas.auth_schema import LoginReq, RefreshTokenReq, TokenRes
from app.schemas.base_schema import AppBaseResponse
from app.schemas.password_reset_schema import (
    ForgetPasswordReq,
    MessageResponse,
    ResetPasswordReq,
    VerifyOTPReq,
    VerifyOTPRes,
)
from app.schemas.user_schema import UserCreateReq, UserRes, user_to_res
from app.services import auth_service, password_reset_service
from app.services.mail_service import send_welcome_email
from app.utils.cookie import clear_auth_cookies, set_auth_cookies

router = APIRouter(prefix="/auth", tags=["Auth"])


# Identify client request from Mobile or Web
def _body_token(request: Request) -> bool:
    """Mobile -> return token in body."""
    return request.headers.get("X-Client", "").lower() == "mobile"


# Register
@router.post(
    "/register", status_code=HTTPStatus.CREATED, response_model=AppBaseResponse[UserRes]
)
async def register(
    data: UserCreateReq,
    uow: IUnitOfWork = Depends(get_uow),
    background_tasks: BackgroundTasks = None,
):
    async with uow:
        user = await auth_service.register(uow, data)

    # Sent welcome mail
    background_tasks.add_task(send_welcome_email, email=user.email, name=user.name)
    return AppBaseResponse(data=user, message="Registration successful.")


# Login
@router.post(
    "/login",
    status_code=HTTPStatus.OK,
    response_model=AppBaseResponse[TokenRes],
)
async def login(
    data: LoginReq,
    request: Request,
    response: Response,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        res = await auth_service.login(uow, data.email, data.password)

    # WEB: set token into HttpOnly cookie
    set_auth_cookies(response, res.access_token, res.refresh_token)

    # MOBILE: if request from website, not contain token in response
    if not _body_token(request):
        res = res.model_copy(update={"access_token": None, "refresh_token": None})

    return AppBaseResponse(data=res, message="Login successful")


# Get current user profile
@router.get(
    "/me",
    status_code=HTTPStatus.OK,
    response_model=AppBaseResponse[UserRes],
)
async def me(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the authenticated user.
    - Web: token from HttpOnly cookie
    - Mobile: token from Authorization header
    """
    return AppBaseResponse(
        data=user_to_res(current_user), message="Get profile successful"
    )


# Request reset password
@router.post(
    "/request-password-reset", status_code=HTTPStatus.OK, response_model=MessageResponse
)
async def request_password_reset(
    data: ForgetPasswordReq, uow: IUnitOfWork = Depends(get_uow)
):
    async with uow:
        message = await password_reset_service.request_password_reset(
            uow, data.email, data.method
        )
    return MessageResponse(message=message)


# Verify OTP (Mobile only)
@router.post("/verify-otp", status_code=HTTPStatus.OK, response_model=VerifyOTPRes)
async def verify_otp(
    data: VerifyOTPReq,
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Mobile: Verify OTP if true -> Create new reset_token.
    """
    async with uow:
        res = await password_reset_service.verify_otp(uow, data.email, data.otp_code)
    return res


# Verify Reset Token and change password
@router.post("/reset-password", status_code=HTTPStatus.OK, response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordReq,
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Reset new password by reset_token
    - Mobile: token from verify-otp
    - Web: token from link email
    """

    async with uow:
        message = await password_reset_service.reset_password(
            uow, data.reset_token, data.new_password
        )
    return MessageResponse(message=message)


# Refresh token
@router.post("/refresh-token", status_code=HTTPStatus.OK, response_model=TokenRes)
async def refresh(
    data: RefreshTokenReq,
    request: Request,
    response: Response,
    uow: IUnitOfWork = Depends(get_uow),
):
    # Get refresh token from cookies
    raw = request.cookies.get(config.REFRESH_COOKIE_NAME) or (
        data.refresh_token if data else None
    )
    if not raw:
        raise InvalidRefreshTokenError("Missing refresh token")

    async with uow:
        res = await auth_service.refresh_token(uow, raw)

    # WEB: set token into cookies
    set_auth_cookies(response, res.access_token, res.refresh_token)

    # MOBILE: if request from website, not contain token in response
    if not _body_token(request):
        res = res.model_copy(update={"access_token": None, "refresh_token": None})

    return res


# Logout
@router.post("/logout", status_code=HTTPStatus.OK, response_model=MessageResponse)
async def logout(
    data: RefreshTokenReq | None,
    request: Request,
    response: Response,
    uow: IUnitOfWork = Depends(get_uow),
):
    # Get token in cookies
    raw = request.cookies.get(config.REFRESH_COOKIE_NAME) or (
        data.refresh_token if data else None
    )
    if raw:
        async with uow:
            await auth_service.logout(uow, raw)

    # Clear cookies
    clear_auth_cookies(response)
    return MessageResponse(message="Logged out successfully")
