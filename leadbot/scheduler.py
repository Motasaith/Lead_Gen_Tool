import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from main import run_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler(timezone="UTC")


def job():
    log.info("Cron tick — starting run_all()")
    asyncio.create_task(run_all())


def main():
    scheduler.add_job(job, IntervalTrigger(hours=6), id="leadbot_run", replace_existing=True)
    scheduler.start()
    log.info("LeadBot scheduler started — running every 6 hours. Ctrl+C to stop.")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
