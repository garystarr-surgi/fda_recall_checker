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
# This is the recommended approach - supervisor handles log file writing
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr

# Alternative: Use file logging if logs directory exists and is writable
# Uncomment below and comment out the above if you prefer file logging
# log_dir = os.path.join(os.path.dirname(__file__), "logs")
# try:
#     os.makedirs(log_dir, exist_ok=True)
#     if os.access(log_dir, os.W_OK):
#         accesslog = os.path.join(log_dir, "access.log")
#         errorlog = os.path.join(log_dir, "error.log")
#     else:
#         # Fall back to stdout/stderr if not writable
#         accesslog = "-"
#         errorlog = "-"
# except (OSError, PermissionError):
#     # Fall back to stdout/stderr if directory can't be created
#     accesslog = "-"
#     errorlog = "-"

