#!/bin/bash
# Force update script - kills processes and updates
# Run: sudo ./force_update.sh

echo "=== Force Updating FDA Recall Checker ==="
echo ""

cd /opt/fda_recall_checker

echo "1. Stopping supervisor..."
sudo supervisorctl stop fda_recall_checker

echo "2. Waiting for processes to stop..."
sleep 3

echo "3. Checking for remaining Python processes..."
PYTHON_PIDS=$(ps aux | grep '[p]ython.*fda_recall_checker' | awk '{print $2}')
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "Found Python processes, killing them..."
    sudo kill -9 $PYTHON_PIDS 2>/dev/null
    sleep 2
fi

echo "4. Checking for gunicorn processes..."
GUNICORN_PIDS=$(ps aux | grep '[g]unicorn.*fda_recall_checker' | awk '{print $2}')
if [ ! -z "$GUNICORN_PIDS" ]; then
    echo "Found gunicorn processes, killing them..."
    sudo kill -9 $GUNICORN_PIDS 2>/dev/null
    sleep 2
fi

echo "5. Checking file permissions..."
ls -la fetch_fda_recalls.py

echo "6. Making file writable..."
sudo chmod 666 fetch_fda_recalls.py 2>/dev/null

echo "7. Pulling latest changes..."
git pull origin main

echo "8. Restoring file permissions..."
sudo chmod 644 fetch_fda_recalls.py

echo "9. Restarting application..."
sudo supervisorctl start fda_recall_checker

echo "10. Checking status..."
sleep 2
sudo supervisorctl status fda_recall_checker

echo ""
echo "=== Update Complete ==="

