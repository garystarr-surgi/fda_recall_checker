import frappe
import requests
import re
from frappe.utils import getdate

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000  # FDA max

def scrub(text):
    """Convert text to a safe docname."""
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text[:140]  # prevent overly long names


@frappe.whitelist()
def fetch_fda_recalls():
    try:
        # ────────────────────────────────────────────────
        # 1. Find newest stored recall date
        # ────────────────────────────────────────────────
        last_date = frappe.db.sql("""
            SELECT MAX(recall_date) FROM `tabFDA Device Recall`
        """)[0][0]

        total_fetched = 0
        skip = 0

        while True:
            params = {"limit": BATCH_SIZE, "skip": skip}

            # FDA requires YYYYMMDD format
            if last_date:
                params["search"] = f"event_date_posted:>{last_date.strftime('%Y%m%d')}"

            response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for item in results:
                # Correct FDA fields
                recall_number = item.get("product_res_number")        # recall number
                device_name = item.get("product_description") or "Unknown Device"
                product_code = item.get("cfres_id")
                report_date = item.get("event_date_posted")          # recall date
                reason = item.get("reason_for_recall")
                status = item.get("recall_status")
                recall_firm = item.get("recalling_firm")
                code_info = item.get("code_info")

                if not recall_number:
                    continue

                # Build unique docname
                doc_name = f"{scrub(device_name)}-{scrub(recall_number)}"

                # Skip existing
                if frappe.db.exists("FDA Device Recall", doc_name):
                    continue

                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name
                doc.recall_number = recall_number
                doc.device_name = device_name[:140]
                doc.product_code = product_code
                doc.recall_date = report_date
                doc.reason = (reason or "")[:140]
                doc.status = status
                doc.recall_firm = (recall_firm or "")[:140]
                doc.code_info = (code_info or "")[:140]

                doc.save(ignore_permissions=True)
                total_fetched += 1

            skip += BATCH_SIZE

        frappe.db.commit()
        return f"Imported {total_fetched} new recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
