from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import get_uow
from app.logging.logger import logger
from app.services.order_service import cancel_expired_orders

scheduler = AsyncIOScheduler()


# Def to call cancel_expired_orders()
async def run_cancel_expired_orders_job() -> None:
    async with get_uow() as uow:
        cancelled = await cancel_expired_orders(uow)
    logger.info("Expired order job done | cancelled=%s", cancelled)


# Def to run the order scheduler once in every 30s
def start_order_scheduler() -> None:
    scheduler.add_job(
        run_cancel_expired_orders_job,
        trigger=IntervalTrigger(seconds=30),
        id="cancel_expired_orders",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info("Order scheduler started")


# Def to shutdown order scheduler
def shutdown_order_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Order scheduler stopped")
