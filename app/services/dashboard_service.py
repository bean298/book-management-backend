from app.db.database import IUnitOfWork
from app.enum.common import PeriodStatus
from app.schemas.dashboard_schema import RevenueRes


# Revenue by period
async def get_revenue_by_period(
    uow: IUnitOfWork, period: PeriodStatus = PeriodStatus.DAY
) -> RevenueRes:
    revenue = await uow.order.revenue_by_period(period)

    return RevenueRes(revenue=revenue)
