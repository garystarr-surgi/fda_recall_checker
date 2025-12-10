#!/usr/bin/env python3
"""
Quick script to check database statistics
Run: python3 check_db.py
"""
from app import app, init_db
from models import FDADeviceRecall

with app.app_context():
    total = FDADeviceRecall.query.count()
    print(f"Total recalls in database: {total}")
    
    # Get some stats
    if total > 0:
        latest = FDADeviceRecall.query.order_by(
            FDADeviceRecall.recall_date.desc()
        ).first()
        oldest = FDADeviceRecall.query.order_by(
            FDADeviceRecall.recall_date.asc()
        ).first()
        
        print(f"Latest recall date: {latest.recall_date if latest.recall_date else 'N/A'}")
        print(f"Oldest recall date: {oldest.recall_date if oldest.recall_date else 'N/A'}")
        
        # Count by status
        from database import db
        by_status = db.session.query(
            FDADeviceRecall.status,
            db.func.count(FDADeviceRecall.id)
        ).group_by(FDADeviceRecall.status).all()
        
        print("\nRecalls by status:")
        for status, count in by_status:
            print(f"  {status or 'Unknown'}: {count}")

