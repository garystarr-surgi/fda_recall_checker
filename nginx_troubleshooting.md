# Nginx Troubleshooting - Seeing "Welcome to nginx!" Instead of App

If you see the default nginx welcome page, it means nginx is running but not configured correctly to proxy to your Flask app.

## Step 1: Check if Flask App is Running

```bash
# Check supervisor status
sudo supervisorctl status fda_recall_checker

# If not running, check logs
sudo tail -50 /var/log/fda_recall_checker.log
sudo tail -50 /var/log/fda_recall_checker_error.log
```

## Step 2: Verify Nginx Configuration

Check if your nginx site is enabled:

```bash
# List enabled sites
ls -la /etc/nginx/sites-enabled/

# Check if your config exists
ls -la /etc/nginx/sites-available/fda_recall_checker
```

## Step 3: Check Nginx Configuration File

```bash
sudo cat /etc/nginx/sites-available/fda_recall_checker
```

It should look like this:

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

## Step 4: Enable Your Site

If the config exists but isn't enabled:

```bash
# Create symlink to enable the site
sudo ln -s /etc/nginx/sites-available/fda_recall_checker /etc/nginx/sites-enabled/

# Remove default nginx site (optional, but recommended)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Step 5: Check if Flask App is Listening

Test if the Flask app is running on port 5000:

```bash
# Check if port 5000 is listening
sudo netstat -tlnp | grep 5000
# Or
sudo ss -tlnp | grep 5000

# Test directly
curl http://127.0.0.1:5000
```

If curl works but browser doesn't, it's an nginx config issue.

## Step 6: Check Nginx Error Logs

```bash
sudo tail -50 /var/log/nginx/error.log
```

## Step 7: Common Issues

### Issue: Default site is still active
```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

### Issue: Wrong server_name
Make sure `server_name` in your config matches your IP or use `_` to accept all:

```nginx
server_name _;  # Accepts all server names
```

### Issue: Flask app not running
```bash
# Start the app
sudo supervisorctl start fda_recall_checker
sudo supervisorctl status fda_recall_checker
```

### Issue: Port 5000 not accessible
Check firewall:
```bash
sudo ufw status
# Make sure port 80 is open (not 5000 - nginx handles that)
```

## Quick Fix Script

Run this to fix common issues:

```bash
#!/bin/bash
# Remove default nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Ensure your site is enabled
sudo ln -sf /etc/nginx/sites-available/fda_recall_checker /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t && sudo systemctl reload nginx

# Check app status
sudo supervisorctl status fda_recall_checker

# Test app directly
curl http://127.0.0.1:5000
```

