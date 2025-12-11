#!/usr/bin/env python3
"""
Migration script to add recall_check_history table
Run this once to create the new table
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import RecallCheckHistory

def migrate():
    """Create the recall_check_history table"""
    with app.app_context():
        print("Creating recall_check_history table...")
        db.create_all()
        print("✓ Migration complete!")
        
        # Check if table was created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'recall_check_history' in tables:
            print("✓ recall_check_history table exists")
            
            # Show table structure
            columns = inspector.get_columns('recall_check_history')
            print("\nTable columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ Table was not created!")

if __name__ == '__main__':
    migrate()
