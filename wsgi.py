"""
WSGI entry point for production deployment
"""
from app import app, init_db

# Initialize database
init_db()

# Start scheduler (only if not already running)
try:
    from scheduler import start_scheduler
    scheduler = start_scheduler()
except Exception as e:
    print(f"Warning: Could not start scheduler: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

