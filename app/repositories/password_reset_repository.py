from datetime import UTC, datetime

from sqlalchemy import delete, select

from app.models.password_reset_model import PasswordResetToken
from app.orm.repository import Repository


class PasswordResetTokenRepository(Repository[PasswordResetToken]):
    def __init__(self, session):
        super().__init__(session, PasswordResetToken)

    # Delete password reset by user_id
    async def delete_by_user_id(self, user_id: str) -> None:
        stmt = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        await self.session.execute(stmt)

    # Find valid OTP
    async def find_valid_otp(self, user_id: str, otp_code: str) -> PasswordResetToken:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used == False,  # noqa: E712
            PasswordResetToken.expires_at > datetime.now(UTC),
            PasswordResetToken.otp_code == otp_code,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
