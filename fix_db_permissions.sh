#!/bin/bash
# Script to fix database file permissions
# Run this on your Ubuntu server

echo "Fixing database file permissions..."

DB_FILE="/opt/fda_recall_checker/fda_recalls.db"
DB_DIR="/opt/fda_recall_checker"

# Check if database exists
if [ -f "$DB_FILE" ]; then
    echo "Database file exists: $DB_FILE"
    
    # Get current permissions
    ls -la "$DB_FILE"
    
    # Fix permissions - make writable by www-data or your user
    # Option 1: If using www-data user
    sudo chown www-data:www-data "$DB_FILE"
    sudo chmod 664 "$DB_FILE"
    
    # Option 2: If using your own user (uncomment and adjust username)
    # sudo chown your-username:your-username "$DB_FILE"
    # sudo chmod 664 "$DB_FILE"
    
    echo "✓ Database file permissions fixed"
else
    echo "Database file does not exist yet. It will be created when the app runs."
    echo "Making sure the directory is writable..."
    
    # Make sure the directory is writable
    sudo chown -R www-data:www-data "$DB_DIR"
    # Or if using your user:
    # sudo chown -R $USER:$USER "$DB_DIR"
    
    echo "✓ Directory permissions set"
fi

# Also fix the directory permissions
sudo chmod 755 "$DB_DIR"

echo ""
echo "Done! The database should now be writable."
echo ""
echo "If you're using www-data user, verify with:"
echo "  sudo -u www-data touch $DB_FILE.test && sudo -u www-data rm $DB_FILE.test"
echo ""
echo "If that works, the permissions are correct."

