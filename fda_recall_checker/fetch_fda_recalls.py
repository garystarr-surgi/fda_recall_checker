# fetch_fda_recalls.py

import frappe
import requests
from frappe.utils import getdate

@frappe.whitelist()
def fetch_fda_recalls():
    """
    Fetch FDA medical device recalls from the openFDA API
    and save them into the 'FDA Device Recall' doctype.
    Avoids duplicates by checking the recall_number field.
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
                # Skip records with no recall number
                continue

            # Check if a record with this recall_number already exists
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

            # Map fields from API safely
            doc.device_name   = item.get("product_description")
            doc.manufacturer  = item.get("manufacturer_name")
            doc.product_code  = item.get("product_code")
            doc.reason        = item.get("reason_for_recall")
            doc.status        = item.get("status")
            doc.recall_firm   = item.get("recalling_firm")
            doc.code_info     = item.get("code_info")

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
            frappe.logger().info(f"Imported FDA Recall: {recall_number} - {doc.device_name}")

        frappe.db.commit()
        return f"Imported {imported_count} recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
