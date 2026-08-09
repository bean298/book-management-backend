from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID
from app.enum.common import UserRole
from app.models.user_model import User
from app.utils.security import hash_password


class UserCreateReq(BaseModel):
    """Schema for register User"""

    email: EmailStr = Field(..., description="Email of user")
    password: str = Field(..., min_length=6, description="Password")
    name: str = Field(..., description="User name")
    role: UserRole = Field(
        default=UserRole.CUSTOMER, description="User role (admin / customer)"
    )


class UserRes(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    created_at: datetime


def req_to_user(data: UserCreateReq) -> User:
    return User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )


def user_to_res(user: User) -> UserRes:
    return UserRes(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        created_at=user.created_at,
    )
