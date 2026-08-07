from app.orm.repository import Repository
from app.models.category_model import Category


class CategoryRepository(Repository[Category]):
    def __init__(self, session):
        super().__init__(session, Category)
