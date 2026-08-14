from app.orm.repository import Repository
from app.models.refresh_token_model import RefreshToken
from sqlalchemy import select, update
from app.models.refresh_token_model import RefreshToken


class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, session):
        super().__init__(session, RefreshToken)

    # Get refresh token by token hash
    async def get_by_hash(self, token_hash: str) -> RefreshToken:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Update refresh token
    async def revoke_all_by_user(self, user_id: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        await self.session.execute(stmt)

    # Revoke a refresh token
    async def revoke(self, token: RefreshToken, replaced_by: str | None = None) -> None:
        token.revoked = True
        if replaced_by:
            token.replaced_by = replaced_by
