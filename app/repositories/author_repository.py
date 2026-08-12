from app.orm.repository import Repository
from app.models.author_model import Author
from sqlalchemy import select


class AuthorRepository(Repository[Author]):
    def __init__(self, session):
        super().__init__(session, Author)

    # Def to get author by name
    async def get_author_by_name(self, author_name: str) -> Author:
        stmt = select(Author).where(Author.name == author_name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
