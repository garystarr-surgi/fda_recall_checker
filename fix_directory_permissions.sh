#!/bin/bash
# Fix directory permissions - run this first
# Run: sudo bash fix_directory_permissions.sh

echo "=== Fixing Directory Permissions ==="
echo ""

DIR="/opt/fda_recall_checker"
CURRENT_USER=$(whoami)

echo "Current user: $CURRENT_USER"
echo "Directory: $DIR"
echo ""

# Check current ownership
echo "Current ownership:"
ls -ld "$DIR"
echo ""

# Fix ownership to current user (or surgiadmin if that's the user)
if [ "$CURRENT_USER" = "root" ]; then
    # If running as root, check who should own it
    if id "surgiadmin" &>/dev/null; then
        OWNER="surgiadmin"
    else
        OWNER=$(stat -c '%U' "$DIR")
    fi
else
    OWNER="$CURRENT_USER"
fi

echo "Setting ownership to: $OWNER"
sudo chown -R $OWNER:$OWNER "$DIR"
sudo chmod -R 755 "$DIR"

# Make sure files are writable
sudo find "$DIR" -type f -exec chmod 644 {} \;
sudo find "$DIR" -type d -exec chmod 755 {} \;

# Make scripts executable
sudo find "$DIR" -name "*.sh" -exec chmod +x {} \;

echo ""
echo "New ownership:"
ls -ld "$DIR"
echo ""
echo "=== Permissions Fixed ==="
echo "Now try: cd $DIR && git pull origin main"

