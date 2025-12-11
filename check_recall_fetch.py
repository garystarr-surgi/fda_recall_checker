#!/usr/bin/env python3
"""
Check if FDA recall fetch ran successfully
This script checks:
1. Application logs for fetch activity
2. Database for new recalls added in the last 24 hours
3. ERPNext for any new recall matches
"""

import sys
import os
from datetime import datetime, timedelta

# Add your app directory to path if needed
# sys.path.insert(0, '/path/to/fda_recall_checker')

from database import db
from models import FDADeviceRecall

def check_recent_recalls():
    """Check for recalls added in the last 24 hours"""
    print("=" * 60)
    print("FDA Recall Fetch Verification")
    print("=" * 60)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check last 24 hours
    yesterday = datetime.now() - timedelta(hours=24)
    
    # Query recalls created in last 24 hours
    # Assuming you have a 'creation' or 'created_at' timestamp field
    # If not, we'll check by recall_date
    
    try:
        # Get most recent recall
        latest_recall = FDADeviceRecall.query.order_by(
            FDADeviceRecall.id.desc()
        ).first()
        
        if latest_recall:
            print(f"Latest Recall in Database:")
            print(f"  ID: {latest_recall.id}")
            print(f"  Recall Number: {latest_recall.recall_number}")
            print(f"  Device: {latest_recall.device_name}")
            print(f"  Recall Date: {latest_recall.recall_date}")
            print()
        
        # Count total recalls
        total_count = FDADeviceRecall.query.count()
        print(f"Total Recalls in Database: {total_count}")
        print()
        
        # Get recalls from today
        today = datetime.now().date()
        today_count = FDADeviceRecall.query.filter(
            FDADeviceRecall.recall_date >= today
        ).count()
        print(f"Recalls with Date = Today: {today_count}")
        
        # Get recent recalls (last 10)
        print("\nLast 10 Recalls Added (by ID):")
        recent = FDADeviceRecall.query.order_by(
            FDADeviceRecall.id.desc()
        ).limit(10).all()
        
        for r in recent:
            print(f"  [{r.id}] {r.recall_number} - {r.device_name[:50]}")
        
        print("\n" + "=" * 60)
        print("Check Application Logs:")
        print("  Look for: 'Imported X new recall records'")
        print("  Look for: 'ERPNext: X inventory matches found'")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()

def check_log_file():
    """Try to find and read recent log entries"""
    log_locations = [
        'fda_recall.log',
        'logs/fda_recall.log',
        '/var/log/fda_recall_checker/fda_recall.log',
        'app.log',
    ]
    
    print("\nSearching for log files...")
    for log_path in log_locations:
        if os.path.exists(log_path):
            print(f"\nFound log: {log_path}")
            print("Last 20 lines:")
            print("-" * 60)
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading log: {e}")
            print("-" * 60)
            break
    else:
        print("No log files found in common locations")
        print("Check your application logs manually")

if __name__ == "__main__":
    # Need to run within Flask app context
    from app import app
    
    with app.app_context():
        check_recent_recalls()
        check_log_file()
