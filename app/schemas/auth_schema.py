from pydantic import BaseModel, EmailStr
from app.schemas.user_schema import UserRes, user_to_res
from app.models.user_model import User


class TokenRes(BaseModel):
    """Return token when login"""

    access_token: str
    token_type: str = "bearer"
    user: UserRes


class LoginReq(BaseModel):
    email: EmailStr
    password: str


# Convert ORM model → Pydantic schema for JSON response
def token_to_res(access_token: str, user: User) -> TokenRes:
    return TokenRes(
        access_token=access_token,
        user=user_to_res(user),
    )
