#!/bin/bash
# Safe update script - stops app, pulls changes, restarts
# Run: sudo ./update_app.sh

echo "=== Updating FDA Recall Checker ==="
echo ""

cd /opt/fda_recall_checker

echo "1. Stopping application..."
sudo supervisorctl stop fda_recall_checker

echo "2. Pulling latest changes..."
git pull origin main

echo "3. Restarting application..."
sudo supervisorctl start fda_recall_checker

echo "4. Checking status..."
sleep 2
sudo supervisorctl status fda_recall_checker

echo ""
echo "=== Update Complete ==="

