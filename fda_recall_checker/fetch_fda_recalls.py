import frappe
import requests
import re
from datetime import datetime

FDA_RECALL_URL = "https://api.fda.gov/device/recall.json"
BATCH_SIZE = 1000


def scrub(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text


@frappe.whitelist()
def fetch_fda_recalls():
    try:
        # Get most recent recall_date we have stored
        last_date = frappe.db.sql("""
            SELECT MAX(recall_date) FROM `tabFDA Device Recall`
        """)[0][0]

        last_search_date = last_date.strftime("%Y%m%d") if last_date else None

        total_fetched = 0
        skip = 0

        while True:
            params = {"limit": BATCH_SIZE, "skip": skip}

            # FDA searches ONLY work on report_date
            if last_search_date:
                params["search"] = f"report_date:>{last_search_date}"

            response = requests.get(FDA_RECALL_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            for item in results:

                recall_number = item.get("product_res_number")
                device_name = item.get("product_description") or "Unknown Device"
                report_date = item.get("report_date")
                event_date_posted = item.get("event_date_posted")

                # Skip if recall number is missing
                if not recall_number:
                    continue

                # Build unique document name
                doc_name = f"{scrub(device_name)}-{recall_number}"

                if frappe.db.exists("FDA Device Recall", doc_name):
                    continue

                # Determine recall_date (use FDA report_date, fallback to event_date_posted)
                if report_date:
                    recall_date = report_date
                else:
                    recall_date = event_date_posted  # fallback because FDA allows no search here

                doc = frappe.new_doc("FDA Device Recall")
                doc.name = doc_name

                # Map fields exactly as you requested
                doc.recall_number = item.get("product_res_number")
                doc.device_name = item.get("product_description")
                doc.product_code = item.get("cfres_id")
                doc.recall_date = recall_date
                doc.reason = item.get("reason_for_recall")
                doc.status = item.get("recall_status")
                doc.recall_firm = item.get("recalling_firm")

                code_info = item.get("code_info")
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
