# Troubleshooting Guide

## Supervisor Exiting Immediately (Exit Status 1)

If supervisor shows "exited: fda_recall_checker (exit status 1; not expected)" repeatedly, the application is crashing on startup. Follow these steps:

### Step 1: Check Error Logs

```bash
# Check the error log file
sudo tail -50 /var/log/fda_recall_checker_error.log

# Check supervisor log
sudo tail -50 /var/log/supervisor/supervisord.log

# If error log doesn't exist, check stdout log
sudo tail -50 /var/log/fda_recall_checker.log
```

### Step 2: Test Imports Manually

Run the test script to identify import errors:

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 test_imports.py
```

Or test manually:

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 -c "from app import app; print('OK')"
```

### Step 3: Test Gunicorn Directly

Try running gunicorn manually to see the actual error:

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
/opt/fda_recall_checker/venv/bin/gunicorn -c /opt/fda_recall_checker/gunicorn_config.py wsgi:app
```

This will show you the exact error message.

### Step 4: Common Issues and Fixes

**Issue: ImportError or ModuleNotFoundError**
```bash
# Make sure you're in the right directory
cd /opt/fda_recall_checker

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: Database initialization error**
```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 -c "from app import app, init_db; init_db()"
```

**Issue: Missing dependencies**
```bash
cd /opt/fda_recall_checker
source venv/bin/activate
pip install Flask Flask-SQLAlchemy requests APScheduler gunicorn python-dotenv
```

**Issue: Permission error on database file (readonly database)**

If you see `sqlite3.OperationalError: attempt to write a readonly database`:

```bash
# Fix database file permissions
sudo chown www-data:www-data /opt/fda_recall_checker/fda_recalls.db
sudo chmod 664 /opt/fda_recall_checker/fda_recalls.db

# Also fix directory permissions
sudo chown -R www-data:www-data /opt/fda_recall_checker
sudo chmod 755 /opt/fda_recall_checker

# Verify the user can write to the database
sudo -u www-data touch /opt/fda_recall_checker/fda_recalls.db.test
sudo -u www-data rm /opt/fda_recall_checker/fda_recalls.db.test

# Or use the provided script
chmod +x fix_db_permissions.sh
sudo ./fix_db_permissions.sh
```

**If using your own user instead of www-data:**
```bash
sudo chown $USER:$USER /opt/fda_recall_checker/fda_recalls.db
sudo chmod 664 /opt/fda_recall_checker/fda_recalls.db
```

**Issue: Circular import or app context error**
Make sure `wsgi.py` properly initializes the app context before importing scheduler.

### Step 5: Run Debug Script

Use the debug script to check everything:

```bash
cd /opt/fda_recall_checker
chmod +x debug_startup.sh
./debug_startup.sh
```

### Step 6: Temporary Fix - Run Without Scheduler

If the scheduler is causing issues, temporarily modify `wsgi.py` to comment out the scheduler:

```python
# Start scheduler (only if not already running)
try:
    from scheduler import start_scheduler
    # scheduler = start_scheduler()  # Comment this out temporarily
    pass
except Exception as e:
    print(f"Warning: Could not start scheduler: {e}")
```

Then test again.

## Supervisor Spawn Error

If you get a "spawn error" when running `sudo supervisorctl start fda_recall_checker`, try these solutions:

### 1. Check Supervisor Configuration

Verify the supervisor config file exists and has correct paths:

```bash
sudo cat /etc/supervisor/conf.d/fda_recall_checker.conf
```

### 2. Verify Paths Exist

Check that all paths in the config actually exist:

```bash
# Check if virtual environment exists
ls -la /opt/fda_recall_checker/venv/bin/gunicorn

# Check if gunicorn_config.py exists
ls -la /opt/fda_recall_checker/gunicorn_config.py

# Check if wsgi.py exists
ls -la /opt/fda_recall_checker/wsgi.py

# Check if directory exists
ls -la /opt/fda_recall_checker/app.py
```

### 3. Test Gunicorn Command Manually

Try running the gunicorn command directly to see the actual error:

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
/opt/fda_recall_checker/venv/bin/gunicorn -c /opt/fda_recall_checker/gunicorn_config.py wsgi:app
```

### 4. Fix Common Issues

**Issue: Gunicorn not installed**
```bash
cd /opt/fda_recall_checker
source venv/bin/activate
pip install gunicorn
```

**Issue: Wrong Python path**
Make sure the virtual environment is using the correct Python:

```bash
which python3
/opt/fda_recall_checker/venv/bin/python3 --version
```

**Issue: Permissions**
```bash
# Make sure www-data (or your user) can access the files
sudo chown -R www-data:www-data /opt/fda_recall_checker
# Or if using your user:
sudo chown -R $USER:$USER /opt/fda_recall_checker
```

**Issue: Directory path wrong**
Make sure `app.py` is in `/opt/fda_recall_checker/`, NOT in `/opt/fda_recall_checker/fda_recall_checker/`

```bash
# This should show app.py
ls /opt/fda_recall_checker/app.py

# If app.py is in a subdirectory, that's the problem!
```

### 5. Updated Supervisor Config

If paths are correct, try this updated supervisor config:

```ini
[program:fda_recall_checker]
command=/opt/fda_recall_checker/venv/bin/gunicorn -c /opt/fda_recall_checker/gunicorn_config.py wsgi:app
directory=/opt/fda_recall_checker
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fda_recall_checker.log
stderr_logfile=/var/log/fda_recall_checker_error.log
environment=PATH="/opt/fda_recall_checker/venv/bin:/usr/local/bin:/usr/bin:/bin"
```

Then reload:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fda_recall_checker
```

### 6. Check Logs

Check supervisor logs for detailed error messages:

```bash
# Supervisor main log
sudo tail -f /var/log/supervisor/supervisord.log

# Application log
sudo tail -f /var/log/fda_recall_checker.log

# Error log (if configured)
sudo tail -f /var/log/fda_recall_checker_error.log
```

### 7. Alternative: Run as Your User

If permissions are an issue, try running as your user instead of www-data:

```ini
[program:fda_recall_checker]
command=/opt/fda_recall_checker/venv/bin/gunicorn -c /opt/fda_recall_checker/gunicorn_config.py wsgi:app
directory=/opt/fda_recall_checker
user=your-username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fda_recall_checker.log
environment=PATH="/opt/fda_recall_checker/venv/bin:/usr/local/bin:/usr/bin:/bin"
```

### 8. Verify File Structure

The correct structure should be:
```
/opt/fda_recall_checker/
├── app.py              ← Flask app (must be here!)
├── wsgi.py             ← WSGI entry point
├── models.py
├── routes.py
├── gunicorn_config.py
├── venv/               ← Virtual environment
│   └── bin/
│       └── gunicorn    ← Must exist here
└── fda_recall_checker/ ← Old Frappe code (can ignore)
```

If `app.py` is inside `fda_recall_checker/` subdirectory, that's the problem!

### 9. Quick Test

Run this to verify everything is set up correctly:

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 -c "import gunicorn; print('Gunicorn OK')"
python3 -c "from app import app; print('App OK')"
```

If both work, the supervisor config should work too.

