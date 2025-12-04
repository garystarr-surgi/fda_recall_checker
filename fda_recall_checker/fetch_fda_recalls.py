import frappe
import requests
import re

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000  # max per request


def scrub(text):
    """Convert text to lowercase, replace spaces with underscores, remove non-alphanum."""
    text = text.lower().strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text


@frappe.whitelist()
def fetch_fda_recalls():
    try:
        # Get latest recall_date from our records
        last_date = frappe.db.sql("""
            SELECT MAX(recall_date) FROM `tabFDA Device Recall`
        """)[0][0]

        total_fetched = 0
        skip = 0

        while True:
            params = {"limit": BATCH_SIZE, "skip": skip}

            if last_date:
                # ⚠ FDA API only supports searching by report_date
                params["search"] = f"report_date:>{last_date.strftime('%Y%m%d')}"

            response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            for item in results:

                # Map fields EXACTLY as you specified
                recall_number = item.get("product_res_number")
                device_name = item.get("product_description") or "Unknown Device"
                product_code = item.get("cfres_id")
                posted_date = item.get("event_date_posted")
                reason = item.get("reason_for_recall")
                status = item.get("recall_status")
                recall_firm = item.get("recalling_firm")
                code_info = item.get("code_info")

                # --- skip if no recall number ---
                if not recall_number:
                    continue

                # Generate unique doc name
                doc_name = f"{scrub(device_name)}-{recall_number}"

                # Skip duplicates
                if frappe.db.exists("FDA Device Recall", doc_name):
                    continue

                # Create new document
                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name
                doc.recall_number = recall_number
                doc.device_name = device_name
                doc.product_code = product_code
                doc.recall_date = posted_date  # stored as recall_date
                doc.reason = reason
                doc.status = status
                doc.recall_firm = recall_firm

                # Truncate ONLY code_info if needed
                if code_info and len(code_info) > 140:
                    doc.code_info = code_info[:140]
                else:
                    doc.code_info = code_info

                doc.save(ignore_permissions=True)
                total_fetched += 1

            skip += BATCH_SIZE

        frappe.db.commit()
        return f"Imported {total_fetched} new recall records"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FDA Recall Fetch Failed")
        return f"Error: {str(e)}"
