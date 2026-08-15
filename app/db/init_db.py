import asyncio
from sqlalchemy import text
from app.db.database import database
from app.orm.postgres import Base
from app.configs.config import AUTH_SCHEMA, BOOK_SCHEMA, COMMERCE_SCHEMA
from app.models.user_model import User
from app.models.category_model import Category
from app.models.author_model import Author
from app.models.book_model import Book
from app.models.password_reset_model import PasswordResetToken
from app.models.refresh_token_model import RefreshToken
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem


async def init_db():
    async with database.engine.begin() as conn:
        # Create schemas if they don't exist
        for schema in [AUTH_SCHEMA, BOOK_SCHEMA, COMMERCE_SCHEMA]:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


def main():
    asyncio.run(init_db())


if __name__ == "__main__":
    main()
