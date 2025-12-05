#!/bin/bash
# Debug script to test application startup
# Run this on your Ubuntu server to identify the issue

echo "=== Testing FDA Recall Checker Startup ==="
echo ""

cd /opt/fda_recall_checker

echo "1. Checking Python version..."
python3 --version
echo ""

echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
    echo "Python path: $(which python3)"
else
    echo "✗ Virtual environment not found!"
    exit 1
fi
echo ""

echo "3. Checking if gunicorn is installed..."
if [ -f "venv/bin/gunicorn" ]; then
    echo "✓ Gunicorn found"
    venv/bin/gunicorn --version
else
    echo "✗ Gunicorn not found! Installing..."
    pip install gunicorn
fi
echo ""

echo "4. Checking if required files exist..."
files=("app.py" "wsgi.py" "models.py" "routes.py" "database.py" "gunicorn_config.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file NOT FOUND!"
    fi
done
echo ""

echo "5. Testing Python imports..."
python3 -c "from app import app; print('✓ App import successful')" 2>&1
if [ $? -ne 0 ]; then
    echo "✗ App import failed!"
    echo "Trying to see the error:"
    python3 -c "from app import app" 2>&1
    exit 1
fi
echo ""

echo "6. Testing database initialization..."
python3 -c "from app import app, init_db; init_db(); print('✓ Database initialization successful')" 2>&1
if [ $? -ne 0 ]; then
    echo "✗ Database initialization failed!"
    python3 -c "from app import app, init_db; init_db()" 2>&1
fi
echo ""

echo "7. Testing gunicorn command (dry run)..."
venv/bin/gunicorn --check-config -c gunicorn_config.py wsgi:app 2>&1
if [ $? -ne 0 ]; then
    echo "✗ Gunicorn config check failed!"
    exit 1
fi
echo ""

echo "8. Testing actual gunicorn startup (will run for 5 seconds)..."
timeout 5 venv/bin/gunicorn -c gunicorn_config.py wsgi:app 2>&1 || echo "Gunicorn started (timeout expected)"
echo ""

echo "=== Debug Complete ==="
echo "If all checks passed, the issue might be with supervisor configuration."
echo "Check the error log: sudo tail -f /var/log/fda_recall_checker_error.log"

