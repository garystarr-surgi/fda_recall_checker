# fetch_fda_recalls.py

import frappe
import requests
from frappe.utils import getdate
import uuid

@frappe.whitelist()
def fetch_fda_recalls():
    """
    Fetch FDA medical device recalls and save them into the
    'FDA Device Recall' doctype. Always creates new docs if necessary.
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
            # Generate unique name if recall_number is missing
            doc_name = recall_number or str(uuid.uuid4())

            # Check if doc already exists
            doc = frappe.get_doc("FDA Device Recall") if not frappe.db.exists("FDA Device Recall", doc_name) else frappe.get_doc("FDA Device Recall", doc_name)

            if not doc:
                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name

            # Map fields
            doc.recall_number = recall_number
            doc.device_name = item.get("product_description")
            doc.manufacturer = item.get("manufacturer_name")
            doc.product_code = item.get("product_code")
            doc.reason = item.get("reason_for_recall")
            doc.status = item.get("status")
            doc.recall_firm = item.get("recalling_firm")
            doc.code_info = item.get("code_info")

            # Convert report_date safely
            report_date = item.get("report_date")
            if report_date:
                try:
                    doc.recall_date = getdate(str(report_date))
                except Exception:
                    doc.recall_date = None

            # Save doc safely
            doc.flags.ignore_mandatory = True
            doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)

            imported_count += 1

            # Optional: log each imported recall
            frappe.logger().info(f"Imported FDA Recall: {doc_name} - {doc.device_name}")

        frappe.db.commit()
        return f"Imported {imported_count} recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
