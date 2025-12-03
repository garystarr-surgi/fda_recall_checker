# fetch_fda_recalls.py

import frappe
import requests
from frappe.utils import getdate
import uuid

@frappe.whitelist()
def fetch_fda_recalls():
    """
    Fetch FDA medical device recalls from openFDA and store in FDA Device Recall DocType.
    Uses res_event_number as unique ID.
    Logs raw items for debugging.
    """
    FDA_RECALL_URL = "https://api.fda.gov/device/recall.json?limit=100"

    try:
        response = requests.get(FDA_RECALL_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            frappe.log_error("FDA Recall API returned no results", "FDA Recall Fetch")
            return "No results found"

        imported_count = 0

        for idx, item in enumerate(results, start=1):
            # Log raw item for debugging
            frappe.log_error(f"Item {idx}: {item}", "FDA Recall Raw Data")

            # Use res_event_number as unique recall_number
            recall_number = item.get("res_event_number")
            if not recall_number:
                recall_number = f"NO_NUMBER_{uuid.uuid4().hex[:8]}"

            # Check if document exists
            existing = frappe.get_all(
                "FDA Device Recall",
                filters={"recall_number": recall_number},
                fields=["name"]
            )
            if existing:
                doc = frappe.get_doc("FDA Device Recall", existing[0].name)
            else:
                doc = frappe.new_doc("FDA Device Recall")
                doc.recall_number = recall_number

            # Map fields from API to DocType
            doc.device_name   = item.get("product_description")
            doc.manufacturer  = item.get("recalling_firm")
            doc.product_code  = item.get("product_code")
            doc.reason        = item.get("reason_for_recall")
            doc.status        = item.get("recall_status")
            doc.recall_firm   = item.get("recalling_firm")
            doc.code_info     = item.get("code_info")

            # Use event_date_posted for recall_date if available
            report_date = item.get("event_date_posted")
            if report_date:
                try:
                    doc.recall_date = getdate(str(report_date))
                except Exception:
                    doc.recall_date = None

            # Save document
            doc.flags.ignore_mandatory = True
            doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)
            imported_count += 1

        frappe.db.commit()
        return f"Imported {imported_count} recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
