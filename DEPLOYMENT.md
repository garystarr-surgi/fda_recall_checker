# FDA Recall Checker - Deployment Guide

This guide will help you deploy the FDA Recall Checker on an Ubuntu server and access it from a Windows machine.

## Prerequisites

- Ubuntu 20.04 or later
- Python 3.8 or later
- Internet connection for FDA API access

## Step 1: Install Python and Dependencies

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install additional system dependencies
sudo apt install -y nginx supervisor
```

## Step 2: Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/fda_recall_checker
sudo chown $USER:$USER /opt/fda_recall_checker

# Copy application files to /opt/fda_recall_checker
# (You can use git, scp, or any file transfer method)
```

## Step 3: Create Virtual Environment

```bash
cd /opt/fda_recall_checker
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Create a `.env` file (optional, for production settings):

```bash
cd /opt/fda_recall_checker
nano .env
```

Add the following (adjust as needed):

```
DATABASE_URL=sqlite:///fda_recalls.db
SECRET_KEY=your-secret-key-here-change-this
FLASK_ENV=production
```

## Step 5: Initialize Database

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 -c "from app import app, init_db; init_db()"
```

## Step 6: Test the Application

```bash
cd /opt/fda_recall_checker
source venv/bin/activate
python3 run.py
```

Visit `http://your-server-ip:5000` from your Windows machine to verify it works.

Press Ctrl+C to stop the test server.

## Step 7: Set Up Gunicorn (Production Server)

Create a Gunicorn configuration file:

```bash
cd /opt/fda_recall_checker
nano gunicorn_config.py
```

Add:

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
```

## Step 8: Configure Supervisor (Process Manager)

Create supervisor configuration:

```bash
sudo nano /etc/supervisor/conf.d/fda_recall_checker.conf
```

Add:

```ini
[program:fda_recall_checker]
command=/opt/fda_recall_checker/venv/bin/gunicorn -c /opt/fda_recall_checker/gunicorn_config.py wsgi:app
directory=/opt/fda_recall_checker
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fda_recall_checker.log
environment=PATH="/opt/fda_recall_checker/venv/bin"
```

Reload supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fda_recall_checker
```

Check status:

```bash
sudo supervisorctl status fda_recall_checker
```

## Step 9: Configure Nginx (Web Server)

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/fda_recall_checker
```

Add:

```nginx
server {
    listen 80;
    server_name your-server-ip-or-domain;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase timeouts for long-running requests
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/fda_recall_checker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 10: Configure Firewall

```bash
# Allow HTTP traffic
sudo ufw allow 80/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Step 11: Access from Windows

1. Find your Ubuntu server's IP address:
   ```bash
   hostname -I
   ```

2. From your Windows machine, open a web browser and navigate to:
   ```
   http://your-server-ip
   ```

3. You should see the FDA Recall Checker dashboard.

## Step 12: Initial Data Fetch

1. Click the "Fetch New Recalls" button in the web interface, OR
2. SSH into the server and run:
   ```bash
   cd /opt/fda_recall_checker
   source venv/bin/activate
   python3 -c "from fetch_fda_recalls import fetch_fda_recalls; print(fetch_fda_recalls())"
   ```

## Step 13: Verify Scheduler

The scheduler is configured to run daily at 2:00 AM. Check logs:

```bash
tail -f /var/log/fda_recall_checker.log
```

## Troubleshooting

### Check Application Status
```bash
sudo supervisorctl status fda_recall_checker
sudo supervisorctl tail -f fda_recall_checker
```

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo supervisorctl restart fda_recall_checker
sudo systemctl restart nginx
```

### Database Location
The SQLite database is located at:
```
/opt/fda_recall_checker/fda_recalls.db
```

### Manual Database Backup
```bash
cd /opt/fda_recall_checker
cp fda_recalls.db fda_recalls.db.backup
```

## Optional: Set Up HTTPS (SSL)

For production, consider setting up SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## API Endpoints

The application also provides REST API endpoints:

- `GET /api/recalls` - List all recalls (with pagination)
- `GET /api/recalls/<id>` - Get specific recall
- `GET /api/stats` - Get statistics
- `POST /fetch` - Manually trigger recall fetch

## Future: ERPNext Integration

To integrate with ERPNext in the future, you can:
1. Use the REST API endpoints to query recalls
2. Compare product codes or device names with your inventory
3. Set up automated alerts when matches are found

