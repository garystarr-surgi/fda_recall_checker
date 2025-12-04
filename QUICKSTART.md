# Quick Start Guide

## For Local Development (Windows)

1. **Install Python 3.8+** if not already installed

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```powershell
   python init_app.py
   ```

4. **Start the development server:**
   ```powershell
   python run.py
   ```

5. **Open your browser:**
   - Navigate to `http://localhost:5000`
   - Click "Fetch New Recalls" to import data

## For Ubuntu Server Deployment

### Step 1: Transfer Files to Ubuntu

From your Windows machine, use one of these methods:

**Option A: Using SCP (if you have SSH access)**
```powershell
# Install WinSCP or use PowerShell SSH
scp -r * user@ubuntu-server:/opt/fda_recall_checker/
```

**Option B: Using Git**
```bash
# On Ubuntu server
cd /opt
git clone <your-repo-url> fda_recall_checker
```

**Option C: Manual Copy**
- Use FileZilla or similar FTP client
- Copy all files to `/opt/fda_recall_checker/` on Ubuntu

### Step 2: Follow Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Ubuntu setup instructions.

### Step 3: Access from Windows

Once deployed, access the application from your Windows browser:
```
http://your-ubuntu-server-ip
```

## Initial Data Fetch

After setup, you can fetch FDA recalls in two ways:

1. **Via Web Interface:**
   - Click "Fetch New Recalls" button in the web UI

2. **Via Command Line:**
   ```bash
   python -c "from fetch_fda_recalls import fetch_fda_recalls; print(fetch_fda_recalls())"
   ```

## Troubleshooting

### Port Already in Use
If port 5000 is in use, change it in `run.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Database Errors
Delete `fda_recalls.db` and reinitialize:
```bash
rm fda_recalls.db
python init_app.py
```

### Import Errors
Make sure you're in the project directory and all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

- Review the [README.md](README.md) for API documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Plan ERPNext integration using the REST API endpoints

