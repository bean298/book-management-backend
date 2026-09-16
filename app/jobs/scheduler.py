from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.jobs.order_jobs import register_order_jobs
from app.jobs.token_jobs import register_token_jobs

scheduler = AsyncIOScheduler()


# Start all jobs
def start_all_jobs() -> None:

    # Register all jobs
    register_order_jobs(scheduler)
    register_token_jobs(scheduler)

    scheduler.start()
    print("All schedulers started")


# Shutdown all jobs
def shutdown_all_jobs() -> None:
    scheduler.shutdown(wait=False)
    print("All schedulers stopped")
