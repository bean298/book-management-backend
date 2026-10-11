from app.db.database import IUnitOfWork
from app.enum.common import PeriodStatus
from app.schemas.dashboard_schema import NewUsersRes, RevenueRes


# Revenue by period
async def get_revenue_by_period(
    uow: IUnitOfWork, period: PeriodStatus = PeriodStatus.DAY
) -> RevenueRes:
    revenue = await uow.order.revenue_by_period(period)

    return RevenueRes(revenue=revenue)


# New users by period
async def get_new_users_by_period(
    uow: IUnitOfWork, period: PeriodStatus = PeriodStatus.DAY
) -> NewUsersRes:
    users = await uow.users.count_new_users_by_period(period)
    return NewUsersRes(users=users)
