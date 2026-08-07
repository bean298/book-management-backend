from app.orm.repository import Repository
from app.models.password_reset_model import PasswordResetToken


class PasswordResetTokenRepository(Repository[PasswordResetToken]):
    def __init__(self, session):
        super().__init__(session, PasswordResetToken)
