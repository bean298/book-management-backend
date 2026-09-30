from datetime import datetime

from pydantic import BaseModel


class Revenue(BaseModel):
    period: datetime
    revenue: float


class RevenueRes(BaseModel):
    revenue: list[Revenue]
