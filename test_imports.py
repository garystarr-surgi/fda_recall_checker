#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
Run this to identify import errors before starting with supervisor
"""
import sys

print("Testing imports...")
print("=" * 50)

try:
    print("1. Testing database import...")
    from database import db
    print("   ✓ database.py imported")
except Exception as e:
    print(f"   ✗ Error importing database: {e}")
    sys.exit(1)

try:
    print("2. Testing models import...")
    from models import FDADeviceRecall
    print("   ✓ models.py imported")
except Exception as e:
    print(f"   ✗ Error importing models: {e}")
    sys.exit(1)

try:
    print("3. Testing app import...")
    from app import app, init_db
    print("   ✓ app.py imported")
except Exception as e:
    print(f"   ✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing routes import...")
    from routes import fetch_recalls_bp, api_bp
    print("   ✓ routes.py imported")
except Exception as e:
    print(f"   ✗ Error importing routes: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Testing fetch_fda_recalls import...")
    from fetch_fda_recalls import fetch_fda_recalls
    print("   ✓ fetch_fda_recalls.py imported")
except Exception as e:
    print(f"   ✗ Error importing fetch_fda_recalls: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Testing wsgi import...")
    from wsgi import app as wsgi_app
    print("   ✓ wsgi.py imported")
except Exception as e:
    print(f"   ✗ Error importing wsgi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("7. Testing database initialization...")
    with app.app_context():
        init_db()
    print("   ✓ Database initialization successful")
except Exception as e:
    print(f"   ✗ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 50)
print("✓ All imports and initialization successful!")
print("The application should be able to start.")

