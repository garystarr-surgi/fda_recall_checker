"""
Gunicorn configuration for production deployment
"""
import os

bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
loglevel = "info"

# Log to stderr/stdout (supervisor will capture these)
# If you want file logging, use a writable directory or create log files with proper permissions
# Option 1: Use app directory (writable by app user)
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
accesslog = os.path.join(log_dir, "access.log")
errorlog = os.path.join(log_dir, "error.log")

# Option 2: Comment out file logging and use stderr/stdout (recommended for supervisor)
# accesslog = "-"  # Log to stdout
# errorlog = "-"   # Log to stderr

