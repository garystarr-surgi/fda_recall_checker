"""
FDA Recall Fetcher - Standalone version
Fetches recalls from FDA API and stores in database
"""
import requests
import re
import json
from datetime import datetime
from database import db
from models import FDADeviceRecall

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000  # max per request

# ERPNext Configuration
ERPNEXT_URL = "https://beta.surgi.shop/api/method/recall_cross_reference.check_inventory"
ERPNEXT_API_KEY = "ae0d7bdc5c61e8b"
ERPNEXT_API_SECRET = "c637ae040a3eae7"

def scrub(text):
    """Convert text to lowercase, replace spaces with underscores, remove non-alphanum"""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text

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

def parse_date(date_str):
    """Parse FDA date string to datetime object"""
    if not date_str:
        return None
    try:
        # FDA dates are typically in YYYYMMDD format
        if len(date_str) == 8 and date_str.isdigit():
            return datetime.strptime(date_str, '%Y%m%d').date()
        # Try other common formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def send_recalls_to_erpnext(recalls_list):
    """
    Send newly fetched recalls to ERPNext for inventory cross-reference
    
    Args:
        recalls_list: List of recall dictionaries to check against inventory
        
    Returns:
        dict with response from ERPNext or error info
    """
    if not recalls_list:
        return {"success": False, "message": "No recalls to send"}
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}'
        }
        
        # Format recalls for ERPNext API
        formatted_recalls = []
        for recall in recalls_list:
            formatted_recalls.append({
                'id': recall.get('id'),
                'recall_number': recall.get('recall_number'),
                'device_name': recall.get('device_name'),
                'product_code': recall.get('product_code'),
                'code_info': recall.get('code_info'),
                'recall_date': recall.get('recall_date').isoformat() if recall.get('recall_date') else None,
                'status': recall.get('status'),
                'reason': recall.get('reason')
            })
        
        response = requests.post(
            ERPNEXT_URL,
            headers=headers,
            json={'recalls': json.dumps(formatted_recalls)},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ ERPNext check complete: {result.get('message', {}).get('matched_count', 0)} matches found")
            return result
        else:
            error_msg = f"ERPNext API error {response.status_code}: {response.text}"
            print(f"✗ {error_msg}")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Error sending to ERPNext: {str(e)}"
        print(f"✗ {error_msg}")
        return {"success": False, "error": error_msg}

def fetch_fda_recalls():
    """Fetch FDA recalls from API and store in database"""
    from flask import has_app_context, current_app
    
    # If we're already in an app context (e.g., called from a route), use it
    # Otherwise, create a new one
    if has_app_context():
        return _fetch_fda_recalls()
    else:
        from app import app
        with app.app_context():
            return _fetch_fda_recalls()

def _fetch_fda_recalls():
    """Internal function that does the actual fetching"""
    new_recalls_for_erpnext = []  # Track new recalls to send to ERPNext
    
    try:
        # Step 1: get the latest recall date we already have
        last_recall = FDADeviceRecall.query.order_by(
            FDADeviceRecall.recall_date.desc()
        ).first()
        
        last_date = last_recall.recall_date if last_recall else None

        # If no recalls exist yet, start from Jan 1, 2024
        if not last_date:
            last_date = datetime(2024, 1, 1).date()

        total_fetched = 0
        skip = 0
        max_skip = 10000  # Safety limit to prevent infinite loops
        consecutive_errors = 0
        max_consecutive_errors = 3

        while skip < max_skip:
            params = {"limit": BATCH_SIZE, "skip": skip}

            if last_date:
                # FDA API uses YYYYMMDD format for dates
                params['search'] = f"event_date_posted:>{last_date.strftime('%Y%m%d')}"

            try:
                response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
                
                # Handle 404 - means no more results available
                if response.status_code == 404:
                    print(f"404 error at skip={skip} - no more results available")
                    break
                
                # Handle other HTTP errors
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                # Reset error counter on success
                consecutive_errors = 0

                if not results:
                    print(f"No more results at skip={skip}")
                    break
                    
            except requests.exceptions.HTTPError as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}), stopping fetch")
                    break
                print(f"HTTP error at skip={skip}: {e}")
                skip += BATCH_SIZE
                continue
            except requests.exceptions.RequestException as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}), stopping fetch")
                    break
                print(f"Request error at skip={skip}: {e}")
                skip += BATCH_SIZE
                continue

            for item in results:
                recall_number = item.get("product_res_number")
                device_name = item.get("product_description") or "Unknown Device"
                code_info = item.get("code_info") or ""
                
                # Extract Model/Catalog Number from code_info first (more reliable), 
                # then fall back to product_description
                model_catalog_number = extract_model_catalog_number(code_info)
                if not model_catalog_number:
                    model_catalog_number = extract_model_catalog_number(device_name)
                
                # Use Model/Catalog Number as product_code if found, otherwise fall back to cfres_id
                product_code = model_catalog_number or item.get("cfres_id")

                doc_name = f"{scrub(device_name)}-{recall_number}"

                # Skip if already exists (use no_autoflush to avoid premature flush errors)
                with db.session.no_autoflush:
                    existing = FDADeviceRecall.query.filter_by(name=doc_name).first()
                    if existing:
                        continue

                # Parse recall date
                event_date = item.get("event_date_posted")
                recall_date = parse_date(event_date) if event_date else None

                # Create new recall record
                # Note: code_info is stored in full (up to 140 chars) to preserve Model/Catalog Number
                code_info_full = item.get("code_info")
                recall = FDADeviceRecall(
                    name=doc_name,
                    recall_number=recall_number,
                    device_name=(device_name[:140] if device_name else None),
                    product_code=product_code[:100] if product_code else None,  # Limit to 100 chars for product_code field
                    recall_date=recall_date,
                    reason=(item.get("reason_for_recall")[:140] if item.get("reason_for_recall") else None),
                    status=item.get("recall_status"),
                    recall_firm=item.get("recalling_firm"),
                    code_info=(code_info_full[:140] if code_info_full else None)
                )

                db.session.add(recall)
                total_fetched += 1
                
                # Add to list for ERPNext checking
                new_recalls_for_erpnext.append({
                    'id': recall.id,
                    'recall_number': recall_number,
                    'device_name': device_name,
                    'product_code': product_code,
                    'code_info': code_info_full,
                    'recall_date': recall_date,
                    'status': item.get("recall_status"),
                    'reason': item.get("reason_for_recall")
                })

            skip += BATCH_SIZE

        db.session.commit()
        
        # Send new recalls to ERPNext for inventory checking
        result_message = f"Imported {total_fetched} new recall records"
        
        if new_recalls_for_erpnext:
            print(f"\n→ Sending {len(new_recalls_for_erpnext)} new recalls to ERPNext for inventory checking...")
            erpnext_result = send_recalls_to_erpnext(new_recalls_for_erpnext)
            
            if erpnext_result.get('success'):
                matched = erpnext_result.get('message', {}).get('matched_count', 0)
                result_message += f"\nERPNext: {matched} inventory matches found"
            else:
                result_message += f"\nERPNext check failed: {erpnext_result.get('error', 'Unknown error')}"
        else:
            print("No new recalls to send to ERPNext")
        
        return result_message

    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Log to console
        return error_msg
    finally:
        pass  # App context will be cleaned up automatically
