import frappe
import requests
from frappe.utils import getdate

FDA_API_URL = "https://api.fda.gov/device/recall.json?limit=100"

def fetch_fda_recalls():
    """
    Fetch FDA Device Recalls and store in ERPNext
    """
    try:
        r = requests.get(FDA_API_URL, timeout=30)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])

        for recall in results:
            recall_number = recall.get("recall_number")
            device_name = recall.get("product_description") or recall.get("device_name")
            manufacturer = recall.get("recalling_firm")
            product_code = recall.get("product_code")
            recall_date = getdate(recall.get("report_date"))
            reason = recall.get("reason_for_recall")
            status = recall.get("status", "Active")

            # Check if recall already exists
            existing = frappe.db.exists("FDA Device Recall", {"recall_number": recall_number})
            if not existing:
                doc = frappe.get_doc({
                    "doctype": "FDA Device Recall",
                    "recall_number": recall_number,
                    "device_name": device_name,
                    "manufacturer": manufacturer,
                    "product_code": product_code,
                    "recall_date": recall_date,
                    "reason": reason,
                    "status": status
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                # After inserting, try to match inventory
                match_inventory(doc)

    except Exception as e:
        frappe.log_error(f"FDA Recall Fetch Error: {str(e)}", "FDA Recall Checker")


def match_inventory(recall_doc):
    """
    Cross-reference recall with ERPNext Item master
    """
    items = frappe.get_all("Item", ["name", "item_name", "item_code", "manufacturer", "description"])
    for item in items:
        match = False
        # Exact match by item_name / product_code
        if item.item_name.lower() == (recall_doc.product_code or "").lower():
            match = True
        # Match by manufacturer + description
        elif item.manufacturer and recall_doc.manufacturer and \
             item.manufacturer.lower() == recall_doc.manufacturer.lower() and \
             recall_doc.device_name.lower() in (item.description or "").lower():
            match = True
        if match:
            recall_doc.matched_item = item.name
            recall_doc.save(ignore_permissions=True)
            frappe.db.commit()
