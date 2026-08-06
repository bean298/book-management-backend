from typing import Generic, TypeVar, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.enum.common import OBJECT_STATUS
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import Select, func
from sqlalchemy import asc, desc, select
from sqlalchemy.sql.elements import ColumnElement  # Represents a conditional expression
from app.schemas.base_schema import AppBasePagingRes
from app.constants.common import MAX_PAGE_SIZE

T = TypeVar("T")


# Apply order_by to stmt
def apply_order_by(
    model,
    stmt: Select,
    order_by: dict[str, int] | None = None,
) -> Select:
    """
    order_by = {
        "created_at": 1,   # ASC
        "name": -1         # DESC
    }
    """

    # If order_by is None or empty, return the original statement
    if not order_by:
        return stmt

    for field_name, direction in order_by.items():
        if not hasattr(model, field_name):
            raise ValueError(f"{model.__name__} has no field '{field_name}'")

        if direction not in (1, -1):
            raise ValueError("Order_by direction must be 1 (asc) or -1 (desc)")

        column: InstrumentedAttribute = getattr(model, field_name)
        stmt = stmt.order_by(asc(column) if direction == 1 else desc(column))

    return stmt


# Class generic repository pattern for database operations
class Repository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    # Add a new object to the database (table) and return the added object
    async def add(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    # Delete an object from the database (table)
    async def delete(self, obj: T):
        await self.session.delete(obj)

    # Get an object by ID
    async def get_by_id(self, id: str) -> T | None:
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == uuid.UUID(id),
                self.model.object_status == OBJECT_STATUS.DELETE.value,
            )
        )
        return result.scalar_one_or_none()

    # Build a SQL statement with conditions, order_by, filters
    def __build_stmt(
        self,
        *conditions: ColumnElement,
        order_by: dict[str, int] | None = None,
        **filters: Any,
    ):
        stmt = select(self.model)

        # Apply conditions
        if conditions:
            stmt = stmt.where(*conditions)

        # Apply filters and validate that the fields exist in the model
        for field, value in filters.items():
            if not hasattr(self.model, field):
                raise ValueError(f"{self.model.__name__} has no field '{field}'")
            stmt = stmt.where(getattr(self.model, field) == value)

        # Apply order_by
        stmt = apply_order_by(self.model, stmt, order_by)

        return stmt

    # List objects with pagination, filtering, and ordering
    async def paginate(
        self,
        *conditions: ColumnElement,
        page: int = 1,
        page_size: int = 20,
        order_by: dict[str, int] | None = None,
        **filters: Any,
    ) -> AppBasePagingRes[T]:
        if page < 1:
            page = 1

        # Max page size
        page_size = min(page_size, MAX_PAGE_SIZE)

        stmt = self.__build_stmt(*conditions, order_by=order_by, **filters)

        # Count total items for pagiantion
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_stmt)

        # Items for the current page
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)

        items = result.scalars().all()

        return AppBasePagingRes[T](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            is_full=page_size * page >= total,
        )
