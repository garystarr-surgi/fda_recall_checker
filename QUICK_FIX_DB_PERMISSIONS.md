# Quick Fix: Database Permissions Issue

If your database file is owned by `surgiadmin` but the app runs as `www-data`, the app can't read/write the database.

## Quick Fix (Choose One):

### Option 1: Change ownership to match app user

First, check what user your app is running as:
```bash
sudo cat /etc/supervisor/conf.d/fda_recall_checker.conf | grep "^user="
```

**If app runs as `www-data`:**
```bash
sudo chown www-data:www-data /opt/fda_recall_checker/fda_recalls.db
sudo chmod 664 /opt/fda_recall_checker/fda_recalls.db
```

**If app runs as `surgiadmin`:**
```bash
# Already correct, but make sure it's readable
sudo chmod 664 /opt/fda_recall_checker/fda_recalls.db
```

### Option 2: Change supervisor to run as surgiadmin

Edit supervisor config:
```bash
sudo nano /etc/supervisor/conf.d/fda_recall_checker.conf
```

Change the `user=` line to:
```ini
user=surgiadmin
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart fda_recall_checker
```

### Option 3: Use the automated script

```bash
cd /opt/fda_recall_checker
git pull origin main
chmod +x fix_db_permissions.sh
sudo ./fix_db_permissions.sh
```

## Verify It Works:

```bash
# Check current ownership
ls -la /opt/fda_recall_checker/fda_recalls.db

# Test if app user can read it
sudo -u www-data python3 -c "import sqlite3; conn = sqlite3.connect('/opt/fda_recall_checker/fda_recalls.db'); print('OK')"
# Or if using surgiadmin:
python3 -c "import sqlite3; conn = sqlite3.connect('/opt/fda_recall_checker/fda_recalls.db'); print('OK')"
```

## After Fixing:

Restart the app:
```bash
sudo supervisorctl restart fda_recall_checker
```

Then refresh your browser - you should see the recalls!

