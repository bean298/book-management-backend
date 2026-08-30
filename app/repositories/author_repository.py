from sqlalchemy import select

from app.models.author_model import Author
from app.orm.repository import Repository


class AuthorRepository(Repository[Author]):
    def __init__(self, session):
        super().__init__(session, Author)

    # Def to get author by name
    async def get_author_by_name(self, author_name: str) -> Author:
        stmt = select(Author).where(Author.name == author_name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
