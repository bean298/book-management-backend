from app.models.category_model import Category
from app.orm.repository import Repository


class CategoryRepository(Repository[Category]):
    def __init__(self, session):
        super().__init__(session, Category)
