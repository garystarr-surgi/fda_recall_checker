# fetch_fda_recalls.py

import frappe
import requests
from frappe.utils import getdate

# Max lengths for fields
MAX_LENGTHS = {
    "recall_number": 140,
    "device_name": 140,
    "manufacturer": 140,
    "product_code": 140,
    "reason": 1000,
    "status": 140,
    "recall_firm": 140,
    "code_info": 1000,
}

@frappe.whitelist()
def fetch_fda_recalls():
    """
    Fetches FDA medical device recalls from openFDA and stores them
    into the FDA Device Recall doctype. Only inserts new recalls.
    Long fields are truncated to prevent DB errors.
    """
    FDA_RECALL_URL = "https://api.fda.gov/device/recall.json?limit=1000"

    try:
        response = requests.get(FDA_RECALL_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            frappe.log_error("FDA Recall API returned no results", "FDA Recall Fetch")
            return "No results found"

        imported_count = 0

        for item in results:
            recall_number = item.get("recall_number")
            if not recall_number:
                continue

            # Only insert if not already in DB
            if frappe.db.exists("FDA Device Recall", {"recall_number": recall_number}):
                continue

            doc = frappe.new_doc("FDA Device Recall")
            
            # Helper function to truncate
            def safe_set(field, value):
                if value:
                    max_len = MAX_LENGTHS.get(field)
                    if max_len:
                        value = str(value)[:max_len]
                    setattr(doc, field, value)

            # Map fields
            safe_set("recall_number", recall_number)
            safe_set("device_name", item.get("product_description"))
            safe_set("manufacturer", item.get("manufacturer_name"))
            safe_set("product_code", item.get("product_code"))
            safe_set("recall_date", item.get("report_date"))
            safe_set("reason", item.get("reason_for_recall"))
            safe_set("status", item.get("status"))

            # Custom fields
            safe_set("recall_firm", item.get("recalling_firm"))
            safe_set("code_info", item.get("code_info"))

            doc.save(ignore_permissions=True)
            imported_count += 1

        frappe.db.commit()
        return f"Imported {imported_count} new recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
