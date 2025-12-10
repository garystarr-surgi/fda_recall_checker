"""
FDA Recall Fetcher - Standalone version
Fetches recalls from FDA API and stores in database
"""
import requests
import re
from datetime import datetime
from database import db
from models import FDADeviceRecall

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000  # max per request

def scrub(text):
    """Convert text to lowercase, replace spaces with underscores, remove non-alphanum"""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text

def extract_model_catalog_number(product_description):
    """Extract Model/Catalog Number from product_description"""
    if not product_description:
        return None
    
    # Look for "Model/Catalog Number" or variations
    patterns = [
        r'Model/Catalog Number[:\s]+([A-Z0-9\s\-]+)',
        r'Model/Catalog[:\s]+Number[:\s]+([A-Z0-9\s\-]+)',
        r'Catalog Number[:\s]+([A-Z0-9\s\-]+)',
        r'Model Number[:\s]+([A-Z0-9\s\-]+)',
        r'Model[:\s]+([A-Z0-9\s\-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, product_description, re.IGNORECASE | re.MULTILINE)
        if match:
            model_number = match.group(1).strip()
            # Clean up - remove extra whitespace, newlines
            model_number = re.sub(r'\s+', ' ', model_number)
            # Take first line if multiple lines
            model_number = model_number.split('\n')[0].strip()
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
                
                # Extract Model/Catalog Number from product_description
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
                recall = FDADeviceRecall(
                    name=doc_name,
                    recall_number=recall_number,
                    device_name=(device_name[:140] if device_name else None),
                    product_code=product_code[:100] if product_code else None,  # Limit to 100 chars for product_code field
                    recall_date=recall_date,
                    reason=(item.get("reason_for_recall")[:140] if item.get("reason_for_recall") else None),
                    status=item.get("recall_status"),
                    recall_firm=item.get("recalling_firm"),
                    code_info=(item.get("code_info")[:140] if item.get("code_info") else None)
                )

                db.session.add(recall)
                total_fetched += 1

            skip += BATCH_SIZE

        db.session.commit()
        return f"Imported {total_fetched} new recall records"

    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Log to console
        return error_msg
    finally:
        pass  # App context will be cleaned up automatically

