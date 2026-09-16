from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import get_uow
from app.logging.logger import logger
from app.services.auth_service import delete_expired_token

scheduler = AsyncIOScheduler()


# Def to call delete_expired_token()
async def run_delete_expired_token_job() -> None:
    async with get_uow() as uow:
        deleted = await delete_expired_token(uow)
    logger.info("Refresh token cleanup done | deleted=%s", deleted)


# Def to run the token scheduler once in every 30s
def start_token_scheduler() -> None:
    scheduler.add_job(
        run_delete_expired_token_job,
        trigger=IntervalTrigger(seconds=30),
        id="delete_expired_token",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info("Refresh token scheduler started")


# Def to shutdown token scheduler
def shutdown_token_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Refresh token scheduler stopped")
