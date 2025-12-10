#!/usr/bin/env python3
"""
Test script to verify Model/Catalog Number extraction
"""
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

# Test with the example
test_text = "Model/Catalog Number: HX-400U-30; UDI: 04953170368615; All Lots which have not expired;"
result = extract_model_catalog_number(test_text)
print(f"Test input: {test_text}")
print(f"Extracted: {result}")
print(f"Expected: HX-400U-30")
print(f"Match: {result == 'HX-400U-30'}")

