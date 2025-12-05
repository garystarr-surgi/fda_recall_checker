#!/bin/bash
# Script to fix log file permissions
# Run this on your Ubuntu server

echo "Fixing log file permissions..."

# Option 1: Create logs directory in app folder (recommended)
mkdir -p /opt/fda_recall_checker/logs
chmod 755 /opt/fda_recall_checker/logs

# Option 2: Create log files in /var/log with proper permissions (if using www-data)
# sudo touch /var/log/fda_recall_checker_access.log
# sudo touch /var/log/fda_recall_checker_error.log
# sudo chown www-data:www-data /var/log/fda_recall_checker*.log
# sudo chmod 644 /var/log/fda_recall_checker*.log

echo "Log directory created at /opt/fda_recall_checker/logs"
echo "You may need to adjust ownership:"
echo "  sudo chown -R www-data:www-data /opt/fda_recall_checker/logs"
echo "  (or use your username instead of www-data)"

