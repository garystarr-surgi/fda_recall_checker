#!/usr/bin/env python3
"""
Migration script to update existing recalls with Model/Catalog Number
extracted from product_description field.

Run: python3 update_existing_product_codes.py
"""
from app import app
from models import FDADeviceRecall
from database import db
import re

def extract_model_catalog_number(text):
    """Extract Model/Catalog Number from text (code_info or product_description)"""
    if not text:
        return None
    
    # Look for "Model/Catalog Number" or variations
    # Pattern: "Model/Catalog Number: HX-400U-30" or "Model/Catalog Number HX-400U-30"
    patterns = [
        r'Model/Catalog Number[:\s]+([A-Z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model/Catalog[:\s]+Number[:\s]+([A-Z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Catalog Number[:\s]+([A-Z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model Number[:\s]+([A-Z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model[:\s]+([A-Z0-9\s\-]+?)(?:;|,|\n|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            model_number = match.group(1).strip()
            # Clean up - remove extra whitespace, newlines
            model_number = re.sub(r'\s+', ' ', model_number)
            # Take first part before semicolon or comma if present
            model_number = model_number.split(';')[0].split(',')[0].strip()
            if model_number:
                return model_number
    
    return None

def update_product_codes():
    """Update product_code for all existing recalls"""
    with app.app_context():
        # Get all recalls
        all_recalls = FDADeviceRecall.query.all()
        total = len(all_recalls)
        
        print(f"Found {total} recalls to process...")
        print("")
        
        updated_count = 0
        skipped_count = 0
        no_model_count = 0
        
        for i, recall in enumerate(all_recalls, 1):
            if i % 100 == 0:
                print(f"Processing {i}/{total}...")
            
            # Skip if already has a product_code that looks like a model number
            # (contains letters and numbers, not just numbers)
            if recall.product_code and re.search(r'[A-Za-z]', recall.product_code):
                skipped_count += 1
                continue
            
            # Extract Model/Catalog Number from code_info first (more reliable),
            # then fall back to device_name
            model_catalog_number = extract_model_catalog_number(recall.code_info)
            if not model_catalog_number:
                model_catalog_number = extract_model_catalog_number(recall.device_name)
            
            if model_catalog_number:
                # Limit to 100 chars to match database field size
                new_product_code = model_catalog_number[:100]
                
                # Only update if different
                if recall.product_code != new_product_code:
                    recall.product_code = new_product_code
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                no_model_count += 1
        
        # Commit all changes
        print("")
        print("Committing changes to database...")
        db.session.commit()
        
        print("")
        print("=== Update Complete ===")
        print(f"Total recalls processed: {total}")
        print(f"Updated with Model/Catalog Number: {updated_count}")
        print(f"Skipped (already correct or no model found): {skipped_count + no_model_count}")
        print(f"  - Already had model number: {skipped_count}")
        print(f"  - No model number found: {no_model_count}")

if __name__ == '__main__':
    print("Starting product code update...")
    print("This will extract Model/Catalog Numbers from device descriptions")
    print("and update the product_code field.")
    print("")
    
    update_product_codes()

