from app.orm.repository import Repository
from app.models.book_model import Book
from sqlalchemy import select


class BookRepository(Repository[Book]):
    def __init__(self, session):
        super().__init__(session, Book)

    # Get book by title
    async def get_book_by_title(self, book_title: str) -> Book:
        stmt = select(Book).where(Book.title == book_title)
        result = await self.session.execute(stmt)
        return result.scalars().first()
