#!/usr/bin/env python3
"""
Test script to debug dashboard issues
Run: python3 test_dashboard.py
"""
from app import app
from models import FDADeviceRecall
from database import db

with app.app_context():
    print("Testing database connection...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    try:
        total = FDADeviceRecall.query.count()
        print(f"✓ Total recalls found: {total}")
        
        if total > 0:
            recent = FDADeviceRecall.query.order_by(
                FDADeviceRecall.recall_date.desc()
            ).limit(10).all()
            print(f"✓ Recent recalls query returned: {len(recent)} records")
            
            if recent:
                print("\nFirst recall:")
                r = recent[0]
                print(f"  ID: {r.id}")
                print(f"  Name: {r.name}")
                print(f"  Device: {r.device_name}")
                print(f"  Date: {r.recall_date}")
        else:
            print("⚠ No recalls found in database!")
            print("  Check if database file exists and has data")
            
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        import traceback
        traceback.print_exc()

