from app.orm.repository import Repository
from app.models.refresh_token_model import RefreshToken
from sqlalchemy import select


class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, session):
        super().__init__(session, RefreshToken)
