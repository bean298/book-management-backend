from fastapi import APIRouter, Depends, Query

from app.api.deps import require_admin
from app.db.database import IUnitOfWork, get_uow
from app.enum.common import PeriodStatus
from app.schemas.base_schema import AppBaseResponse
from app.schemas.dashboard_schema import RevenueRes
from app.services import dashboard_service
from app.utils.common import Error400

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/revenue", summary="Get revenue", response_model=AppBaseResponse[RevenueRes])
async def get_revenue(
    period: PeriodStatus = Query(default=PeriodStatus.DAY),
    uow: IUnitOfWork = Depends(get_uow),
    admin=Depends(require_admin),
):
    try:
        async with uow:
            revenue = await dashboard_service.get_revenue_by_period(uow, period=period)
            return AppBaseResponse(data=revenue)
    except ValueError as ex:
        return Error400(str(ex))
