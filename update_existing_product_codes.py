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
    # Include lowercase letters in the pattern (A-Za-z0-9)
    patterns = [
        r'Model/Catalog Number[:\s]+([A-Za-z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model/Catalog[:\s]+Number[:\s]+([A-Za-z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Catalog Number[:\s]+([A-Za-z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model Number[:\s]+([A-Za-z0-9\s\-]+?)(?:;|,|\n|$)',
        r'Model[:\s]+([A-Za-z0-9\s\-]+?)(?:;|,|\n|$)',
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
            
            # Extract Model/Catalog Number from code_info first (more reliable),
            # then fall back to device_name
            model_catalog_number = extract_model_catalog_number(recall.code_info)
            if not model_catalog_number:
                model_catalog_number = extract_model_catalog_number(recall.device_name)
            
            if model_catalog_number:
                # Limit to 100 chars to match database field size
                new_product_code = model_catalog_number[:100]
                
                # Always update if we found a model number (even if product_code already exists)
                # This ensures we get the Model/Catalog Number instead of cfres_id
                if recall.product_code != new_product_code:
                    # Debug specific record
                    if recall.recall_number == 'Z-0570-2026':
                        print(f"  DEBUG - Updating {recall.recall_number}:")
                        print(f"    Old product_code: {recall.product_code}")
                        print(f"    New product_code: {new_product_code}")
                        print(f"    Code_info: {recall.code_info[:100] if recall.code_info else 'None'}")
                    
                    recall.product_code = new_product_code
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # Debug: show a few examples where model number wasn't found
                if no_model_count < 5 and recall.code_info:
                    print(f"  Debug - No model found in: {recall.code_info[:80]}...")
                # Special debug for the specific record
                if recall.recall_number == 'Z-0570-2026':
                    print(f"  DEBUG - No model found for {recall.recall_number}:")
                    print(f"    Code_info: {repr(recall.code_info)}")
                    print(f"    Device_name: {repr(recall.device_name)}")
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

