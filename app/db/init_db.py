import asyncio

from sqlalchemy import text

from app.configs.config import AUTH_SCHEMA, BOOK_SCHEMA, COMMERCE_SCHEMA
from app.db.database import database
from app.models.author_model import Author  # noqa: F401
from app.models.book_model import Book  # noqa: F401
from app.models.cart_item_model import CartItem  # noqa: F401
from app.models.cart_model import Cart  # noqa: F401
from app.models.category_model import Category  # noqa: F401
from app.models.order_item_model import OrderItem  # noqa: F401
from app.models.order_model import Order  # noqa: F401
from app.models.password_reset_model import PasswordResetToken  # noqa: F401
from app.models.payment_model import Payment  # noqa: F401
from app.models.refresh_token_model import RefreshToken  # noqa: F401
from app.models.user_model import User  # noqa: F401
from app.orm.postgres import Base


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
