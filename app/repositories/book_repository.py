import uuid

from sqlalchemy import select

from app.enum.common import OBJECT_STATUS
from app.models.book_model import Book
from app.orm.repository import Repository


class BookRepository(Repository[Book]):
    def __init__(self, session):
        super().__init__(session, Book)

    # Get book by title
    async def get_book_by_title(self, book_title: str) -> Book:
        stmt = select(Book).where(Book.title == book_title)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Get book by id for update
    async def get_by_id_for_update(self, book_id: str) -> Book | None:
        stmt = (
            select(Book)
            .where(
                Book.id == uuid.UUID(book_id),
                Book.object_status == OBJECT_STATUS.ACTIVE.value,
            )
            # Lock the row to prevent concurrent updates during checkout.
            .with_for_update()
            # Refresh the existing SQLAlchemy objs with the latest data from the database.
            # The object may already exist in the current Session with stale data,
            # so populate_existing=True overwrites it with the latest query result.
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
