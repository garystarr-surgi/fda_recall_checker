"""
Gunicorn configuration for production deployment
"""
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/fda_recall_checker_access.log"
errorlog = "/var/log/fda_recall_checker_error.log"
loglevel = "info"

