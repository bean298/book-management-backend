from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, EmailStr, Field

from app.enum.common import UserRole
from app.models.user_model import User
from app.utils.format_phone import validate_vn_phone
from app.utils.security import hash_password

# Annotated phone
PhoneNumber = Annotated[
    int | None,
    Field(None, description="Vietnamese mobile phone number"),
    AfterValidator(validate_vn_phone),  # Validate phone regex
]


class _UserBase(BaseModel):
    """Shared base fields for User schemas."""

    name: str = Field(..., min_length=1, max_length=255, description="User name")
    email: EmailStr = Field(..., max_length=255, description="Email of user")
    phone: PhoneNumber


class UserCreateReq(_UserBase):
    """Schema for registering a new user."""

    password: str = Field(..., min_length=6, description="Password")
    role: UserRole = Field(
        default=UserRole.CUSTOMER, description="User role (admin / customer)"
    )


class UserRes(_UserBase):
    """Schema for user response."""

    id: UUID
    role: str
    created_at: datetime


class UpdateUserReq(BaseModel):
    """Schema for updating user."""

    name: str | None = Field(None, min_length=1, max_length=255)
    phone: PhoneNumber


def req_to_user(data: UserCreateReq) -> User:
    return User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=data.role,
    )


# Convert ORM model → Pydantic schema for JSON response
def user_to_res(user: User) -> UserRes:
    return UserRes(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        created_at=user.created_at,
    )
