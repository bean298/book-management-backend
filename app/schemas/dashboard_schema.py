from datetime import datetime

from pydantic import BaseModel


class Revenue(BaseModel):
    period: datetime
    revenue: float


class RevenueRes(BaseModel):
    revenue: list[Revenue]


class UserInfo(BaseModel):
    id: str
    name: str
    email: str


class NewUser(BaseModel):
    period: datetime
    users: list[UserInfo]
    count: int


class NewUsersRes(BaseModel):
    users: list[NewUser]
