#!/usr/bin/env python3
"""
Script to delete all recalls and refetch from FDA API
This will ensure all records use the latest extraction logic.

WARNING: This will delete all existing recalls and re-fetch them.
This may take a while depending on how many recalls there are.

Run: python3 refetch_all_recalls.py
"""
from app import app
from models import FDADeviceRecall
from database import db
from fetch_fda_recalls import fetch_fda_recalls

def refetch_all():
    """Delete all recalls and refetch"""
    with app.app_context():
        # Count existing records
        total = FDADeviceRecall.query.count()
        print(f"Current recalls in database: {total}")
        print("")
        
        response = input("Are you sure you want to delete all recalls and refetch? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        print("")
        print("Deleting all existing recalls...")
        
        # Delete all records
        FDADeviceRecall.query.delete()
        db.session.commit()
        
        print(f"✓ Deleted {total} records")
        print("")
        print("Fetching all recalls from FDA API...")
        print("This may take several minutes...")
        print("")
        
        # Fetch all recalls
        result = fetch_fda_recalls()
        
        print("")
        print("=== Refetch Complete ===")
        print(result)
        
        # Count new records
        new_total = FDADeviceRecall.query.count()
        print(f"New total recalls: {new_total}")

if __name__ == '__main__':
    print("=== Refetch All Recalls ===")
    print("")
    print("This will:")
    print("  1. Delete all existing recalls from the database")
    print("  2. Re-fetch all recalls from the FDA API")
    print("  3. Apply the latest Model/Catalog Number extraction logic")
    print("")
    print("WARNING: This will take a while and will temporarily remove all data!")
    print("")
    
    refetch_all()

