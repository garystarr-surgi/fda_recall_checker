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

        total_fetched = 0
        skip = 0

        while True:
            params = {"limit": BATCH_SIZE, "skip": skip}

            if last_date:
                # FDA API uses YYYYMMDD format for dates
                params['search'] = f"event_date_posted:>{last_date.strftime('%Y%m%d')}"

            response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for item in results:

                # New mapping:
                recall_number = item.get("product_res_number")   # Recall Number
                device_name = item.get("product_description") or "Unknown Device"
                doc_name = f"{scrub(device_name)}-{recall_number}"

                # Skip if already exists
                if frappe.db.exists("FDA Device Recall", doc_name):
                    continue

                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name

                # New FDA field → ERPNext field mapping
                doc.recall_number = item.get("product_res_number")
                doc.device_name = item.get("product_description")
                doc.product_code = item.get("cfres_id")              # Product Code
                doc.recall_date = item.get("event_date_posted")       # Report Date
                doc.reason = item.get("reason_for_recall")            # Reason
                doc.status = item.get("recall_status")                # Status
                doc.recall_firm = item.get("recalling_firm")          # Recalling Firm
                doc.code_info = item.get("code_info")                 # Code Info

                # Leave your truncate logic the same
                if doc.reason:
                    doc.reason = doc.reason[:140]

                if doc.code_info:
                    doc.code_info = doc.code_info[:140]

                if doc.device_name:
                    doc.device_name = doc.device_name[:140]

                if doc.recall_firm:
                    doc.recall_firm = doc.recall_firm[:140]

                doc.save(ignore_permissions=True)
                total_fetched += 1

            skip += BATCH_SIZE

        frappe.db.commit()
        return f"Imported {total_fetched} new recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
