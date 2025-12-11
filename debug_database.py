#!/usr/bin/env python3
"""
Debug script to check database contents
"""
import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'instance', 'fda_recalls.db')

print("=" * 70)
print("Database Debug Info")
print("=" * 70)
print(f"Database path: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")
print(f"File size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")
print()

# Connect directly with sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Show all tables
print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")
print()

# Check the fda_device_recall table
try:
    cursor.execute("SELECT COUNT(*) FROM fda_device_recall")
    count = cursor.fetchone()[0]
    print(f"Records in fda_device_recall: {count}")
    print()
    
    if count > 0:
        print("Sample record:")
        cursor.execute("SELECT * FROM fda_device_recall LIMIT 1")
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        for col, val in zip(columns, row):
            print(f"  {col}: {val}")
        
        print()
        print("Recent 5 recalls:")
        cursor.execute("SELECT id, recall_number, device_name FROM fda_device_recall ORDER BY recall_date DESC LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Number: {row[1]}, Device: {row[2][:50]}")
            
except Exception as e:
    print(f"Error querying table: {e}")

conn.close()
