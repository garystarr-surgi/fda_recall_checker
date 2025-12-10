#!/bin/bash
# Script to fix database file permissions and create database if needed
# Run this on your Ubuntu server

echo "Fixing database file permissions..."

DB_FILE="/opt/fda_recall_checker/fda_recalls.db"
DB_DIR="/opt/fda_recall_checker"

# Detect the user running the app (check supervisor config)
if [ -f "/etc/supervisor/conf.d/fda_recall_checker.conf" ]; then
    APP_USER=$(grep "^user=" /etc/supervisor/conf.d/fda_recall_checker.conf | cut -d'=' -f2)
    if [ -z "$APP_USER" ]; then
        APP_USER="www-data"  # Default
    fi
else
    APP_USER="www-data"  # Default
fi

echo "Detected app user: $APP_USER"

# Check if database exists
if [ -f "$DB_FILE" ]; then
    echo "Database file exists: $DB_FILE"
    
    # Get current permissions
    ls -la "$DB_FILE"
    
    # Fix permissions - make writable by www-data or your user
    sudo chown $APP_USER:$APP_USER "$DB_FILE"
    sudo chmod 664 "$DB_FILE"
    
    echo "✓ Database file permissions fixed"
else
    echo "Database file does not exist yet. Creating it with proper permissions..."
    
    # First, make sure the directory is writable by the app user
    sudo chown -R $APP_USER:$APP_USER "$DB_DIR"
    sudo chmod 755 "$DB_DIR"
    
    # Create the database as the app user
    echo "Initializing database as $APP_USER..."
    cd "$DB_DIR"
    sudo -u $APP_USER bash -c "source venv/bin/activate && python3 -c 'from app import app, init_db; init_db()'"
    
    if [ -f "$DB_FILE" ]; then
        echo "✓ Database created successfully"
        ls -la "$DB_FILE"
    else
        echo "⚠ Warning: Database creation may have failed. Check the error above."
        echo "You may need to run: sudo -u $APP_USER bash -c 'cd $DB_DIR && source venv/bin/activate && python3 -c \"from app import app, init_db; init_db()\"'"
    fi
fi

# Ensure directory permissions are correct
sudo chmod 755 "$DB_DIR"

echo ""
echo "Done! Verifying permissions..."
echo ""

# Verify the user can write to the database directory
if sudo -u $APP_USER touch "$DB_DIR/.test_write" 2>/dev/null; then
    sudo -u $APP_USER rm "$DB_DIR/.test_write"
    echo "✓ $APP_USER can write to the directory"
else
    echo "✗ $APP_USER cannot write to the directory - check permissions"
fi

if [ -f "$DB_FILE" ]; then
    if sudo -u $APP_USER touch "$DB_FILE.test" 2>/dev/null; then
        sudo -u $APP_USER rm "$DB_FILE.test"
        echo "✓ $APP_USER can write to the database file"
    else
        echo "✗ $APP_USER cannot write to the database file - check permissions"
    fi
fi

echo ""
echo "If all checks passed, the database should be writable."

