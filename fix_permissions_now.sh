#!/bin/bash
# Quick fix script - run this on your Ubuntu server

echo "=== Fixing Database Permissions ==="
echo ""

DB_FILE="/opt/fda_recall_checker/fda_recalls.db"
DB_DIR="/opt/fda_recall_checker"

# Check what user supervisor is configured to use
if [ -f "/etc/supervisor/conf.d/fda_recall_checker.conf" ]; then
    APP_USER=$(grep "^user=" /etc/supervisor/conf.d/fda_recall_checker.conf | cut -d'=' -f2 | tr -d ' ')
    if [ -z "$APP_USER" ]; then
        APP_USER="www-data"
    fi
else
    APP_USER="www-data"
fi

echo "App user from supervisor config: $APP_USER"
echo ""

# Check current ownership
echo "Current database file ownership:"
ls -la "$DB_FILE"
echo ""

# Fix ownership to match app user
echo "Fixing ownership to $APP_USER..."
sudo chown $APP_USER:$APP_USER "$DB_FILE"
sudo chmod 664 "$DB_FILE"

# Also fix directory permissions
sudo chown -R $APP_USER:$APP_USER "$DB_DIR"
sudo chmod 755 "$DB_DIR"

echo ""
echo "New ownership:"
ls -la "$DB_FILE"
echo ""

# Test if the user can write
echo "Testing write access..."
if sudo -u $APP_USER touch "$DB_FILE.test" 2>/dev/null; then
    sudo -u $APP_USER rm "$DB_FILE.test"
    echo "✓ $APP_USER can write to the database file"
else
    echo "✗ $APP_USER still cannot write - check permissions manually"
    exit 1
fi

echo ""
echo "=== Permissions Fixed! ==="
echo "Now restart the app:"
echo "  sudo supervisorctl restart fda_recall_checker"

