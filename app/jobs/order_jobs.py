from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import get_uow
from app.logging.logger import logger
from app.services.order_service import cancel_expired_orders


# Def to call cancel_expired_orders()
async def run_cancel_expired_orders_job() -> None:
    async with get_uow() as uow:
        cancelled = await cancel_expired_orders(uow)
    logger.info("Expired order job done | cancelled=%s", cancelled)


# Def to run the order scheduler once in every 30s
def register_order_jobs(scheduler: AsyncIOScheduler) -> None:
    scheduler.add_job(
        run_cancel_expired_orders_job,
        trigger=IntervalTrigger(seconds=30),
        id="cancel_expired_orders",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("Order job registered")
