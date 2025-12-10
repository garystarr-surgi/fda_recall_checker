#!/usr/bin/env python3
"""
Debug script to check a specific record and see why it's not updating
"""
from app import app
from models import FDADeviceRecall
from update_existing_product_codes import extract_model_catalog_number

with app.app_context():
    # Find the specific record
    recall = FDADeviceRecall.query.filter_by(recall_number='Z-0570-2026').first()
    
    if not recall:
        print("Record not found!")
        exit(1)
    
    print(f"Recall Number: {recall.recall_number}")
    print(f"Current Product Code: {recall.product_code}")
    print(f"")
    print(f"Code Info (full): {repr(recall.code_info)}")
    print(f"Code Info (length): {len(recall.code_info) if recall.code_info else 0}")
    print(f"")
    print(f"Device Name: {recall.device_name}")
    print(f"")
    
    # Try to extract from code_info
    if recall.code_info:
        extracted = extract_model_catalog_number(recall.code_info)
        print(f"Extracted from code_info: {extracted}")
    else:
        print("code_info is None or empty")
    
    # Try to extract from device_name
    if recall.device_name:
        extracted2 = extract_model_catalog_number(recall.device_name)
        print(f"Extracted from device_name: {extracted2}")
    
    print(f"")
    print(f"Should update: {extracted and extracted != recall.product_code}")

