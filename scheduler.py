"""
Scheduler for automatic FDA recall fetching
Runs daily to fetch new recalls from FDA API
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Import will be done inside function to avoid circular imports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scheduled_fetch():
    """Scheduled task to fetch FDA recalls"""
    from fetch_fda_recalls import fetch_fda_recalls
    logger.info("Starting scheduled FDA recall fetch...")
    try:
        result = fetch_fda_recalls()
        logger.info(f"Scheduled fetch completed: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled fetch: {str(e)}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    # Run daily at 2 AM
    scheduler.add_job(
        scheduled_fetch,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_fda_fetch',
        name='Daily FDA Recall Fetch',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - will fetch FDA recalls daily at 2:00 AM")
    return scheduler

if __name__ == '__main__':
    # For testing - run immediately
    print("Running test fetch...")
    fetch_fda_recalls()
    print("Test fetch completed")

