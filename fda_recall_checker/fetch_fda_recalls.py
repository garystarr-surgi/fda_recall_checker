import frappe
import requests
import re
from frappe.utils import getdate

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000  # max per request

def scrub(text):
    """Convert text to lowercase, replace spaces with underscores, remove non-alphanum"""
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text

@frappe.whitelist()
def fetch_fda_recalls():
    try:
        # Step 1: get the latest recall date we already have
        last_date = frappe.db.sql("""
            SELECT MAX(recall_date) FROM `tabFDA Device Recall`
        """)[0][0]
        
        # If no recalls exist yet, start from Jan 1, 2024
        if not last_date:
            from datetime import datetime
            last_date = datetime(2024, 1, 1)
        
        total_fetched = 0
        skip = 0
        
        while True:
            params = {"limit": BATCH_SIZE, "skip": skip}
            
            if last_date:
                # FDA API uses YYYYMMDD format for dates
                params['search'] = f"event_date_posted:>{last_date.strftime('%Y%m%d')}"
            
            try:
                response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # If we get a 404, we've reached the end of available results
                if e.response.status_code == 404:
                    print(f"Reached end of results at skip={skip}")
                    break
                else:
                    # Re-raise other HTTP errors
                    raise
            
            data = response.json()
            results = data.get("results", [])
            
            # Stop if no results returned
            if not results:
                break
            
            # Check if we've fetched fewer results than requested (last page)
            results_count = len(results)
            
            for item in results:
                recall_number = item.get("product_res_number")
                device_name = item.get("product_description") or "Unknown Device"
                product_code = item.get("cfres_id")
                doc_name = f"{scrub(device_name)}-{recall_number}"
                
                # Skip if already exists
                if frappe.db.exists("FDA Device Recall", doc_name):
                    continue
                
                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name
                doc.recall_number = recall_number
                doc.device_name = device_name
                doc.product_code = product_code
                doc.recall_date = item.get("event_date_posted")
                doc.reason = item.get("reason_for_recall")
                doc.status = item.get("recall_status")
                doc.recall_firm = item.get("recalling_firm")
                doc.code_info = item.get("code_info")
                
                # Truncate fields to avoid "Value too big"
                if doc.reason:
                    doc.reason = doc.reason[:140]
                if doc.code_info:
                    doc.code_info = doc.code_info[:140]
                if doc.device_name:
                    doc.device_name = doc.device_name[:140]
                
                doc.save(ignore_permissions=True)
                total_fetched += 1
            
            # If we got fewer results than requested, we're on the last page
            if results_count < BATCH_SIZE:
                print(f"Last page reached with {results_count} results")
                break
            
            skip += BATCH_SIZE
        
        frappe.db.commit()
        return f"Imported {total_fetched} new recall records"
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
