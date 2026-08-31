"""
database.py: Database & Dependency Injection

Mission:
1. Init the only common instance PostgresDBContext for the whole app
2. Init IUnitOfWork Protocal - to let know what repository must have in UOW
3. Provide get_uow() - factory function to create UnitOfWork for each request
"""

from typing import Protocol, cast, runtime_checkable

from app.configs.config import DATABASE_URL
from app.orm.postgres import PostgresDBContext
from app.orm.unit_of_work import UnitOfWork
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.category_model import CategoryRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.password_reset_repository import (
    PasswordResetTokenRepository,
)
from app.repositories.payment_repository import PaymentRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository

# Connection to database
database = PostgresDBContext(
    connection_string=DATABASE_URL, echo=False, pool_size=10, max_overflow=20
)


@runtime_checkable
class IUnitOfWork(Protocol):
    # Init repository for UOW
    # Call uow.model -> UnitOfWork.__getattr__ will auto create
    # ModelRepository(session)
    users: UserRepository
    categories: CategoryRepository
    authors: AuthorRepository
    books: BookRepository
    password_reset_token: PasswordResetTokenRepository
    refresh_tokens: RefreshTokenRepository
    cart: CartRepository
    cart_items: CartItemRepository
    order: OrderRepository
    order_items: OrderItemRepository
    payment: PaymentRepository

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


# Factory function
def get_uow() -> IUnitOfWork:
    return cast(
        IUnitOfWork,
        UnitOfWork(
            db=database,
            repositories={
                "users": UserRepository,
                "categories": CategoryRepository,
                "authors": AuthorRepository,
                "books": BookRepository,
                "password_reset_token": PasswordResetTokenRepository,
                "refresh_tokens": RefreshTokenRepository,
                "cart": CartRepository,
                "cart_items": CartItemRepository,
                "order": OrderRepository,
                "order_items": OrderItemRepository,
                "payment": PaymentRepository,
            },
        ),
    )
