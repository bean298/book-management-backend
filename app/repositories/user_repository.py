from sqlalchemy import select

from app.models.user_model import User
from app.orm.repository import Repository


class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    # Def to get user by email
    async def get_user_by_email(self, user_email: str) -> User:
        stmt = select(User).where(User.email == user_email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
