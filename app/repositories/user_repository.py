from app.orm.repository import Repository
from app.models.user_model import User


class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(session, User)
