from app.orm.repository import Repository
from app.models.author_model import Author


class AuthorRepository(Repository[Author]):
    def __init__(self, session):
        super().__init__(session, Author)
