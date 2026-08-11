from fastapi import APIRouter, Depends, BackgroundTasks
from app.db.database import get_uow, IUnitOfWork
from app.schemas.user_schema import UserCreateReq, UserRes
from app.schemas.auth_schema import LoginReq, TokenRes
from app.services import auth_service, password_reset_service
from app.services.mail_service import send_welcome_email
from app.schemas.password_reset_schema import (
    MessageResponse,
    ForgetPasswordReq,
    VerifyOTPReq,
    VerifyOTPRes,
    ResetPasswordReq,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# Register
@router.post("/register", response_model=UserRes)
async def register(
    data: UserCreateReq,
    uow: IUnitOfWork = Depends(get_uow),
    background_tasks: BackgroundTasks = None,
):
    async with uow:
        user = await auth_service.register(uow, data)

    # Sent welcome mail
    background_tasks.add_task(send_welcome_email, email=user.email, name=user.name)
    return user


# Login
@router.post("/login", response_model=TokenRes)
async def login(
    data: LoginReq,
    uow: IUnitOfWork = Depends(get_uow),
):
    async with uow:
        res = await auth_service.login(uow, data.email, data.password)
        return res


# Request reset password
@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    data: ForgetPasswordReq, uow: IUnitOfWork = Depends(get_uow)
):
    async with uow:
        message = await password_reset_service.request_password_reset(
            uow, data.email, data.method
        )
    return MessageResponse(message=message)


# Verify OTP (Mobile only)
@router.post("/verify-otp", response_model=VerifyOTPRes)
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
@router.post("/reset-password", response_model=MessageResponse)
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
