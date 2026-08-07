from app.orm.repository import Repository
from app.models.book_model import Book


class BookRepository(Repository[Book]):
    def __init__(self, session):
        super().__init__(session, Book)
