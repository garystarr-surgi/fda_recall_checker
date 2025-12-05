"""
WSGI entry point for production deployment
"""
import sys
import logging

# Set up logging to stderr (supervisor will capture this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

try:
    from app import app, init_db
    logger.info("Successfully imported app")
except Exception as e:
    logger.error(f"Failed to import app: {e}", exc_info=True)
    sys.exit(1)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}", exc_info=True)
    # Don't exit - database might already exist
    pass

# Start scheduler (only if not already running)
try:
    from scheduler import start_scheduler
    scheduler = start_scheduler()
    logger.info("Scheduler started successfully")
except Exception as e:
    logger.warning(f"Could not start scheduler: {e}")
    # Don't exit - scheduler is optional
    pass

# Export app for gunicorn
application = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

