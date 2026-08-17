from app.logging.logger import logger
from app.db.database import IUnitOfWork
from app.exceptions.token_exception import InvalidOTPError
from app.enum.common import ResetMethod
from app.utils.security import generate_otp, create_reset_token, verify_reset_token
from datetime import datetime, timedelta, timezone
from app.models.password_reset_model import PasswordResetToken
from app.services import mail_service
from app.exceptions.resource_exception import NotFoundError
from app.utils.security import hash_password
from app.schemas.password_reset_schema import VerifyOTPRes

OTP_EXPIRE_MINUTES = 5


# Send OTP (MOBILE | WEB )
async def request_password_reset(uow: IUnitOfWork, email: str, method: str) -> str:
    """
    Create OTP or JWT link
    - method="otp" -> Create OTP, sent OTP by email
    - method="link" -> Create JWT, sent email contain URL to change password
    """

    # Check
    user = await uow.users.get_user_by_email(email)
    if not user:
        logger.warning("Password reset requested for non-existent email: %s", email)
        return "If this email is registered, an OTP has been sent"

    await uow.password_reset_token.delete_by_user_id(user_id=user.id)

    # OTP
    if method == ResetMethod.OTP:
        # Create new OTP
        otp_code = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)

        reset_token = PasswordResetToken(
            user_id=user.id,
            otp_code=otp_code,
            method=ResetMethod.OTP,
            expires_at=expires_at,
        )
        await uow.password_reset_token.add(reset_token)
        await uow.commit()

        await mail_service.send_otp_mail(
            email=user.email, name=user.name, otp_code=otp_code
        )
        logger.info("Password reset OTP sent | email=%s", user.email)

    # Link (Web): send email with a link to the reset password page
    elif method == ResetMethod.LINK:
        token = create_reset_token(str(user.id))

        await mail_service.send_reset_link(
            email=user.email,
            name=user.name,
            token=token,
        )
        logger.info("Password reset link sent | email=%s", user.email)

    return "If this email is registered, a reset instruction has been sent."


# Verify OTP (MOBILE)
async def verify_otp(uow: IUnitOfWork, email: str, otp_code: str) -> VerifyOTPRes:
    """
    Authorization OTP and create reset_token (Mobile only)
    - Find user by email -> user_id
    - Find OTP by user_id
    - Validate: OTP existed, not used, not exipered
    - If true -> Create new reset_token
    """

    # Check user
    user = await uow.users.get_user_by_email(email)
    if not user:
        logger.warning("Password reset requested for non-existent email: %s", email)
        return "If this email is registered, an OTP has been sent"

    # Verify OTP
    otp_record = await uow.password_reset_token.find_valid_otp(user.id, otp_code)
    if not otp_record:
        logger.warning("Verify OTP failed: invalid or expired OTP | email=%s", email)
        raise InvalidOTPError()

    otp_record.used = True
    await uow.commit()
    logger.info("OTP verified | user_id=%s", user.id)

    reset_token = create_reset_token(str(user.id))

    return VerifyOTPRes(
        reset_token=reset_token,
        message="OTP verified. Please enter your new password.",
    )


# Reset password (Web + Mobile)
async def reset_password(uow: IUnitOfWork, reset_token: str, new_password: str) -> str:
    """
    Reset new password by reset_token
    - Mobile: token from verify-otp
    - Web: token from link email
    """

    user_id = verify_reset_token(reset_token)

    user = await uow.users.get_by_id(user_id)
    if not user:
        logger.warning("Reset password failed: user not found | user_id=%s", user_id)
        raise NotFoundError()

    user.hashed_password = hash_password(new_password)
    await uow.commit()

    logger.info("Password reset successful for user_id=%s", user_id)
    return "Password has been reset successfully. You can now login."
