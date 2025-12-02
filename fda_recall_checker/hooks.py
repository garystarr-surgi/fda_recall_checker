# hooks.py

app_name = "fda_recall_checker"
app_title = "FDA Recall Checker"
app_publisher = "SurgiShop"
app_description = "FDA Recall Checker"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "gary.starr@surgishop.com"
app_license = "MIT"
app_version = "0.0.1"

# Scheduler: runs daily
scheduler_events = {
    "daily": [
        "fda_recall_checker.fda_recall_checker.fetch_fda_recalls.fetch_fda_recalls"
    ]
}

# Optional: expose fetch function via API
# override_whitelisted_methods = {
#     "fda_recall_checker.fetch_fda_recalls": "fda_recall_checker.fda_recall_checker.fetch_fda_recalls.fetch_fda_recalls"
# }
