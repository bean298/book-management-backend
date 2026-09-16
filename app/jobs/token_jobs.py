from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.database import get_uow
from app.logging.logger import logger
from app.services.auth_service import delete_expired_token


# Def to call delete_expired_token()
async def run_delete_expired_token_job() -> None:
    async with get_uow() as uow:
        deleted = await delete_expired_token(uow)
    logger.info("Refresh token cleanup done | deleted=%s", deleted)


# Def to run the token scheduler once in every 30s
def register_token_jobs(scheduler: AsyncIOScheduler) -> None:
    scheduler.add_job(
        run_delete_expired_token_job,
        trigger=IntervalTrigger(days=6),
        id="delete_expired_token",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("Refresh token job registered")
