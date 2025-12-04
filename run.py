"""
Development server runner with scheduler
"""
from app import app, init_db
from scheduler import start_scheduler

# Initialize database
init_db()

# Start scheduler (optional for development)
# Uncomment to enable automatic fetching
# scheduler = start_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

